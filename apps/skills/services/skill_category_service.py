
from django.db import transaction
from django.core.exceptions import ValidationError
from typing import List, Optional, Dict, Any
from ..models import SkillCategory


class SkillCategoryService:


    @staticmethod
    def get_all_categories(include_inactive: bool = False) -> List[SkillCategory]:

        queryset = SkillCategory.objects.select_related('parent_category')
        
        # For future scalability when we add is_active field
        if not include_inactive and hasattr(SkillCategory, 'is_active'):
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('name')

    @staticmethod
    def get_category_by_id(category_id: str) -> Optional[SkillCategory]:

        try:
            return SkillCategory.objects.select_related(
                'parent_category'
            ).prefetch_related(
                'subcategories',
                'skills'
            ).get(id=category_id)
        except SkillCategory.DoesNotExist:
            return None

    @staticmethod
    def get_root_categories() -> List[SkillCategory]:

        return SkillCategory.objects.filter(
            parent_category__isnull=True
        ).order_by('name')

    @staticmethod
    def get_category_tree() -> List[Dict[str, Any]]:

        root_categories = SkillCategoryService.get_root_categories()
        
        def build_tree(category):
            """Recursively build category tree"""
            return {
                'id': str(category.id),
                'name': category.name,
                'description': category.description,
                'skills_count': category.skills.count(),
                'subcategories': [
                    build_tree(sub) 
                    for sub in category.subcategories.all()
                ]
            }
        
        return [build_tree(cat) for cat in root_categories]

    @staticmethod
    def get_category_path(category: SkillCategory) -> List[SkillCategory]:
 
        path = [category]
        current = category.parent_category
        
        while current:
            path.insert(0, current)
            current = current.parent_category
        
        return path

    @staticmethod
    @transaction.atomic
    def create_category(
        name: str,
        description: Optional[str] = None,
        parent_category_id: Optional[str] = None
    ) -> SkillCategory:
 
        # Validate name
        name = name.strip().title()
        if SkillCategory.objects.filter(name__iexact=name).exists():
            raise ValidationError(
                f"Category with name '{name}' already exists."
            )

        # Validate parent category if provided
        parent_category = None
        if parent_category_id:
            try:
                parent_category = SkillCategory.objects.get(id=parent_category_id)
            except SkillCategory.DoesNotExist:
                raise ValidationError("Parent category not found.")

        # Create category
        category = SkillCategory.objects.create(
            name=name,
            description=description,
            parent_category=parent_category
        )

        return category

    @staticmethod
    @transaction.atomic
    def update_category(
        category_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parent_category_id: Optional[str] = None
    ) -> SkillCategory:
   
        try:
            category = SkillCategory.objects.get(id=category_id)
        except SkillCategory.DoesNotExist:
            raise ValidationError("Category not found.")

        # Update name if provided
        if name:
            name = name.strip().title()
            if SkillCategory.objects.filter(
                name__iexact=name
            ).exclude(id=category_id).exists():
                raise ValidationError(
                    f"Category with name '{name}' already exists."
                )
            category.name = name

        # Update description if provided
        if description is not None:
            category.description = description

        # Update parent if provided
        if parent_category_id is not None:
            if parent_category_id == '':
                category.parent_category = None
            else:
                try:
                    parent = SkillCategory.objects.get(id=parent_category_id)
                    
                    # Prevent circular reference
                    if SkillCategoryService._would_create_cycle(category, parent):
                        raise ValidationError(
                            "Cannot set parent: would create circular reference."
                        )
                    
                    category.parent_category = parent
                except SkillCategory.DoesNotExist:
                    raise ValidationError("Parent category not found.")

        category.save()
        return category

    @staticmethod
    def _would_create_cycle(category: SkillCategory, new_parent: SkillCategory) -> bool:
        
      
        current = new_parent
        while current:
            if current.id == category.id:
                return True
            current = current.parent_category
        return False

    @staticmethod
    @transaction.atomic
    def delete_category(
        category_id: str,
        reassign_to_parent: bool = False
    ) -> Dict[str, Any]:
       
        try:
            category = SkillCategory.objects.prefetch_related(
                'subcategories',
                'skills'
            ).get(id=category_id)
        except SkillCategory.DoesNotExist:
            raise ValidationError("Category not found.")

        subcategories_count = category.subcategories.count()
        skills_count = category.skills.count()

        if reassign_to_parent:
            # Reassign subcategories to this category's parent
            category.subcategories.update(
                parent_category=category.parent_category
            )
            
            # Reassign skills to parent category (if exists)
            if category.parent_category:
                category.skills.update(category=category.parent_category)
            else:
                # If no parent, we need to handle orphaned skills
                if skills_count > 0:
                    raise ValidationError(
                        "Cannot delete root category with skills. "
                        "Please reassign skills first."
                    )

        else:
            # Check if category has children or skills
            if subcategories_count > 0 or skills_count > 0:
                raise ValidationError(
                    f"Cannot delete category with {subcategories_count} "
                    f"subcategories and {skills_count} skills. "
                    "Please move or delete them first, or use reassign option."
                )

        category.delete()

        return {
            'deleted': True,
            'category_id': category_id,
            'reassigned_subcategories': subcategories_count if reassign_to_parent else 0,
            'reassigned_skills': skills_count if reassign_to_parent else 0
        }

    @staticmethod
    def search_categories(query: str) -> List[SkillCategory]:
     
        if not query:
            return []

        return SkillCategory.objects.filter(
            name__icontains=query
        ) | SkillCategory.objects.filter(
            description__icontains=query
        ).distinct().order_by('name')

    @staticmethod
    def get_category_statistics(category_id: str) -> Dict[str, Any]:
       
        try:
            category = SkillCategory.objects.prefetch_related(
                'subcategories',
                'skills',
                'skills__volunteer_skills'
            ).get(id=category_id)
        except SkillCategory.DoesNotExist:
            raise ValidationError("Category not found.")

        # Calculate statistics
        total_skills = category.skills.count()
        total_subcategories = category.subcategories.count()
        
        # Count volunteers with skills in this category
        volunteers_count = sum(
            skill.volunteer_skills.values('volunteer').distinct().count()
            for skill in category.skills.all()
        )

        return {
            'category_id': str(category.id),
            'category_name': category.name,
            'total_skills': total_skills,
            'total_subcategories': total_subcategories,
            'total_volunteers': volunteers_count,
            'depth_level': len(SkillCategoryService.get_category_path(category))
        }