# -*- coding: utf-8 -*-

"""A collection of abbreviations, acronyms and neighborhoods."""


class Library(object):
    """Common items to translate or clean."""

    def __init__(self):
        """The library items."""
        # http://en.wikipedia.org/wiki/Street_or_road_name
        # Street_type_designations
        self.assessor_abbreviations = [
            # Major roads
            ['HIGHWAY', 'HW'],
            ['FREEWAY', ''],
            ['AUTOROUTE', ''],
            ['AUTOBAHN', ''],
            ['EXPRESSWAY', ''],
            ['AUTOSTRASSE', ''],
            ['AUTOSTRADA', ''],
            ['BYWAY', ''],
            ['AUTO-ESTRADA', ''],
            ['MOTORWAY', ''],
            ['PIKE', ''],
            ['AVENUE', 'AV'],
            ['BOULEVARD', 'BL'],
            ['ROAD', 'RD'],
            ['STREET', 'ST'],
            # Small roads
            ['ALLEY', ''],
            ['BAY', ''],
            ['BEND', ''],
            ['DRIVE', 'DR'],
            ['FAIRWAY', ''],
            ['GARDENS', ''],
            ['GATE', ''],
            ['GROVE', ''],
            ['HEIGHTS', ''],
            ['HIGHLANDS', ''],
            ['KNOLL', ''],
            ['LANE', 'LN'],
            ['MANOR', ''],
            ['MEWS', ''],
            ['PATHWAY', ''],
            ['TERRACE', ''],
            ['TRAIL', ''],
            ['VALE', ''],
            ['VIEW', ''],
            ['WALK', ''],
            ['WAY', ''],
            ['WYND', ''],
            # Culs-de-sac
            ['CLOSE', ''],
            ['COURT', 'CT'],
            ['PLACE', 'PL'],
            ['COVE', ''],
            # Shapes
            ['CIRCLE', ''],
            ['CRESCENT', ''],
            ['DIAGONAL', ''],
            ['LOOP', ''],
            ['QUADRANT', ''],
            ['SQUARE', ''],
            # Geographic attributes
            ['HILL', ''],
            ['GRADE', ''],
            ['CAUSEWAY', ''],
            ['CANYON', ''],
            ['RIDGE', ''],
            ['PARKWAY', 'PW'],
            # Functions
            ['ESPLANADE', ''],
            ['APPROACH', ''],
            ['FRONTAGE', ''],
            ['PARADE', ''],
            ['PARK', ''],
            ['PLAZA', ''],
            ['PROMENADE', ''],
            ['QUAY', ''],
            ['BYPASS', ''],
            ['STRAVENUE', ''],

            # Post cleanup
            ['AVE.', 'AV'],
            ['BLVD.', 'BL'],
            ['ROAD', 'RD'],
            ['ST.', 'ST'],
            ['DR.', 'DR']
        ]
        self.acronyms = [
            [' Iii ', ' III '],
            [' Ii ', ' II '],
            [' Iv ', ' IV '],
            [' Xiv ', ' XIV '],
            ['Llc', 'LLC'],
            ['L L C', 'LLC'],
            ['Fbo', 'FBO'],
            ['Pcw85', 'PCW85'],
            ['Nola', 'NOLA'],
            ['NOLAn', 'Nolan'],
            ['Fka', 'FKA'],
            ['Bwe ', 'BWE '],
            ['Mjh', 'MJH'],
            ['Jmh ', 'JMH '],
            ['Gmj', 'GMJ'],
            ['Ctn', 'CTN'],
            ['Ll ', 'LL '],
            ['Co ', 'Co. '],
            ['Jlra', 'JLRA'],
            ['Jsw', 'JSW'],
            ['Jcl', 'JCL'],
            [' And ', ' and '],
            [' Of ', ' of '],
            [' The ', ' the '],
            ['Cdc', 'CDC'],
            ['Bssb', 'BSSB'],
            ['Uv', 'UV']
        ]
        self.abbreviations = [
            ['Jr', 'Jr.'],
            ['Sr', 'Sr.'],
            ['St ', 'St. '],
            ['Dr ', 'Dr. ']
        ]
        self.mc_names = [
            ['Mca', 'McA'],
            ['Mcb', 'McB'],
            ['Mcc', 'McC'],
            ['Mcd', 'McD'],
            ['Mce', 'McE'],
            ['Mcf', 'McF'],
            ['Mcg', 'McG'],
            ['Mch', 'McH'],
            ['Mci', 'McI'],
            ['Mcj', 'McJ'],
            ['Mck', 'McK'],
            ['Mcl', 'McL'],
            ['Mcm', 'McM'],
            ['Mcn', 'McN'],
            ['Mco', 'McO'],
            ['Mcp', 'McP'],
            ['Mcq', 'McQ'],
            ['Mcr', 'McR'],
            ['Mcs', 'McS'],
            ['Mct', 'McT'],
            ['Mcu', 'McU'],
            ['Mcv', 'McV'],
            ['Mcw', 'McW'],
            ['Mcx', 'McX'],
            ['Mcy', 'McY'],
            ['Mcz', 'McZ']
        ]
        self.streets = [
            ['Blvd', 'Blvd.'],
            ['Blvd,', 'Blvd.,'],
            ['Boulevard', 'Blvd.'],
            ['Hwy', 'Highway'],
            [' Rd', ' Road'],
            ['Ct', 'Court'],
            ['Ave,', 'Ave.,'],
            ['Avenue', 'Ave.'],
            [' To ', ' to '],

            ['1St', '1st'],
            ['2Nd', '2nd'],
            ['3Rd', '3rd'],
            ['4Th', '4th'],
            ['5Th', '5th'],
            ['6Th', '6th'],
            ['7Th', '7th'],
            ['8Th', '8th'],
            ['9Th', '9th'],
            ['0Th', '0th']
        ]
        """
        Not sure what to do for "St.". This --> [' St', ' St.'] would also
        pick up something such as 123 Straight Road. The same could
        conceivably happen with "Ave". "Dr" needs to become "Drive", but have
        the same problem
        """
        self.middle_initials = [
            [' A ', ' A. '],
            [' B ', ' B. '],
            [' C ', ' C. '],
            [' D ', ' D. '],
            [' E ', ' E. '],
            [' F ', ' F. '],
            [' G ', ' G. '],
            [' H ', ' H. '],
            [' I ', ' I. '],
            [' J ', ' J. '],
            [' K ', ' K. '],
            [' L ', ' L. '],
            [' M ', ' M. '],
            [' N ', ' N. '],
            [' O ', ' O. '],
            [' P ', ' P. '],
            [' Q ', ' Q. '],
            [' R ', ' R. '],
            [' S ', ' S. '],
            [' T ', ' T. '],
            [' U ', ' U. '],
            [' V ', ' V. '],
            [' W ', ' W. '],
            [' X ', ' X. '],
            [' Y ', ' Y. '],
            [' Z ', ' Z. ']
        ]
        self.neighborhood_names = [
            ['B. W.', 'B.W.'],
            ['St.  A', 'St. A'],
            ['Mcd', 'McD']
        ]
        self.ordinals = [
            ['1st', '1'],
            ['2nd', '2'],
            ['3rd', '3'],
            ['4th', '4'],
            ['5th', '5'],
            ['6th', '6'],
            ['7th', '7'],
        ]
