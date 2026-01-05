from .base import BaseService
from apps.accounts.models import Address

VALID_WILAYAS = [
    'Adrar', 'Chlef', 'Laghouat', 'Oum El Bouaghi', 'Batna', 'Béjaïa',
    'Biskra', 'Béchar', 'Blida', 'Bouira', 'Tamanrasset', 'Tébessa',
    'Tlemcen', 'Tiaret', 'Tizi Ouzou', 'Alger', 'Djelfa', 'Jijel',
    'Sétif', 'Saïda', 'Skikda', 'Sidi Bel Abbès', 'Annaba', 'Guelma',
    'Constantine', 'Médéa', 'Mostaganem', 'M\'Sila', 'Mascara', 'Ouargla',
    'Oran', 'El Bayadh', 'Illizi', 'Bordj Bou Arréridj', 'Boumerdès',
    'El Tarf', 'Tindouf', 'Tissemsilt', 'El Oued', 'Khenchela', 'Souk Ahras',
    'Tipaza', 'Mila', 'Aïn Defla', 'Naâma', 'Aïn Témouchent', 'Ghardaïa',
    'Relizane', 'Timimoun', 'Bordj Badji Mokhtar', 'Ouled Djellal',
    'Béni Abbès', 'In Salah', 'In Guezzam', 'Touggourt', 'Djanet',
    'El M\'Ghair', 'El Meniaa'
]


class AddressService(BaseService):
    """Handle address operations"""

    @staticmethod
    def validate_wilaya(wilaya):
        """Validate Algerian province"""
        if wilaya not in VALID_WILAYAS:
            raise ValueError('Invalid wilaya. Must be one of the 58 Algerian provinces.')
        return True

    @staticmethod
    def create_or_update_address(profile, address_line_1, city, wilaya, address_line_2='', latitude=None, longitude=None):
        """Create or update address for profile"""
        AddressService.validate_wilaya(wilaya)

        # Check if profile already has an address
        if hasattr(profile, 'address') and profile.address:
            # Update existing address
            address = profile.address
            address.address_line_1 = address_line_1
            address.address_line_2 = address_line_2
            address.city = city
            address.wilaya = wilaya
            address.country = 'Algeria'
            if latitude is not None:
                address.latitude = latitude
            if longitude is not None:
                address.longitude = longitude
            address.save()
            created = False
        else:
            # Create new address
            address = Address.objects.create(
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                city=city,
                wilaya=wilaya,
                country='Algeria',
                latitude=latitude,
                longitude=longitude
            )
            profile.address = address
            profile.save()
            created = True

        action = 'created' if created else 'updated'
        AddressService.log_info(f'Address {action}: {address_line_1}, {city}, {wilaya}')
        return address

    @staticmethod
    def get_full_address(address):
        """Get formatted full address"""
        if not address:
            return None
        
        parts = []
        if address.address_line_1:
            parts.append(address.address_line_1)
        if address.address_line_2:
            parts.append(address.address_line_2)
        if address.city:
            parts.append(address.city)
        if address.wilaya:
            parts.append(address.wilaya)
        if address.country:
            parts.append(address.country)
        
        return ', '.join(parts)

    @staticmethod
    def validate_coordinates(latitude, longitude):
        """Validate geographical coordinates"""
        if latitude is not None:
            if not (-90 <= latitude <= 90):
                raise ValueError('Latitude must be between -90 and 90 degrees')
        
        if longitude is not None:
            if not (-180 <= longitude <= 180):
                raise ValueError('Longitude must be between -180 and 180 degrees')
        
        return True