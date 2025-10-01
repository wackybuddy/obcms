# Technical Reference Documentation

This directory contains technical reference materials, including geographic coordinate systems and data standards used in OBCMS.

## Contents

### Geographic Reference
- **[COORDINATE_SYSTEM.md](COORDINATE_SYSTEM.md)** - Coordinate system overview and usage guide
- **[REGION_IX_COORDINATE_GUIDE.md](REGION_IX_COORDINATE_GUIDE.md)** - Specific coordinate reference for Region IX (Zamboanga Peninsula)

## Geographic Coordinate Systems

OBCMS uses standardized coordinate systems for location data across all modules.

### Primary Coordinate System
- **System:** WGS84 (EPSG:4326)
- **Format:** Decimal degrees
- **Precision:** 6 decimal places (≈0.11 meters)

### Data Standards

#### Location Data Format
```json
{
  "latitude": 7.123456,
  "longitude": 124.123456,
  "elevation": 123.45,
  "coordinate_system": "WGS84"
}
```

#### Administrative Boundaries
- **Region Level:** 2-digit region code (e.g., "09" for Region IX)
- **Province Level:** Full province name with region prefix
- **Municipality Level:** Municipality/city name with province
- **Barangay Level:** Barangay name with complete administrative hierarchy

### Region IX (Zamboanga Peninsula)

Provinces covered:
- Zamboanga del Norte
- Zamboanga del Sur
- Zamboanga Sibugay

**Reference:** [REGION_IX_COORDINATE_GUIDE.md](REGION_IX_COORDINATE_GUIDE.md)

### Region XII (SOCCSKSARGEN)

Provinces covered:
- South Cotabato
- Cotabato (North Cotabato)
- Sultan Kudarat
- Sarangani
- General Santos City

## Data Validation

### Coordinate Validation Rules
1. Latitude: -90 to 90 (Philippines: approximately 4 to 21)
2. Longitude: -180 to 180 (Philippines: approximately 116 to 127)
3. Elevation: -500 to 3000 meters (Philippines: -10 to 2956)

### Geographic Boundaries
- **Philippines Bounding Box:**
  - North: 21.120611
  - South: 4.586126
  - East: 126.604384
  - West: 116.928571

## Geocoding Services

OBCMS integrates with geocoding services for address lookup and coordinate conversion.

### Supported Services
- OpenStreetMap Nominatim
- Google Maps API (optional)
- Philippine PSA location database

## Related Documentation
- [Community Management Module](../product/obcMS-summary.md)
- [MANA Geographic Mapping](../guidelines/OBC_guidelines_mana.md)
- [Data Import Guidelines](../admin-guide/installation.md)

## External Resources
- [WGS84 Coordinate System](https://epsg.io/4326)
- [Philippine Standard Geographic Code](https://psa.gov.ph/classification/psgc/)
- [OpenStreetMap Philippines](https://www.openstreetmap.org/relation/443174)
