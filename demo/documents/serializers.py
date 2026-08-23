from rest_framework import serializers


class AHNUApplicationSerializer(serializers.Serializer):
    """
    Serializer for the Anhui Normal University Application Form.
    These fields map to {{variable}} placeholders in the .doc template.
    """
    # Personal Info
    sur_name = serializers.CharField(max_length=100, help_text="Surname")
    given_name = serializers.CharField(max_length=100, help_text="Given Name")
    chinese_name = serializers.CharField(max_length=100, required=False, default="", allow_blank=True, help_text="Chinese Name")

    # Nationality & Sex
    nationality = serializers.CharField(max_length=100, help_text="Nationality")
    male = serializers.CharField(max_length=10, required=False, default="□", allow_blank=True, help_text="Male checkbox: ☑ or □")
    female = serializers.CharField(max_length=10, required=False, default="□", allow_blank=True, help_text="Female checkbox: ☑ or □")

    # Date of Birth
    birth_year = serializers.CharField(max_length=10, help_text="Birth Year")
    birth_month = serializers.CharField(max_length=10, help_text="Birth Month")
    birth_day = serializers.CharField(max_length=10, help_text="Birth Day")

    # Marital Status
    marital_status = serializers.CharField(max_length=50, required=False, default="", allow_blank=True, help_text="Marital Status")

    # Religion & Place of Birth
    religion = serializers.CharField(max_length=100, required=False, default="", allow_blank=True, help_text="Religion")
    birth_place = serializers.CharField(max_length=200, help_text="Place of Birth")

    # Passport
    passport_no = serializers.CharField(max_length=100, help_text="Passport Number")

    # Education & Occupation
    highest_diploma = serializers.CharField(max_length=200, required=False, default="", allow_blank=True, help_text="Highest Diploma Obtained")
    occupation = serializers.CharField(max_length=200, required=False, default="", allow_blank=True, help_text="Occupation")

    # Address & Contact
    permanent_address = serializers.CharField(max_length=500, help_text="Permanent Address at Home Country")
    phone = serializers.CharField(max_length=50, required=False, default="", allow_blank=True, help_text="Phone number")
    email = serializers.CharField(max_length=200, required=False, default="", allow_blank=True, help_text="Email")
    wechat = serializers.CharField(max_length=100, required=False, default="", allow_blank=True, help_text="WeChat")

    # Reference
    institution = serializers.CharField(max_length=300, required=False, default="", allow_blank=True, help_text="Institution for Reference")
    institution_tel = serializers.CharField(max_length=50, required=False, default="", allow_blank=True, help_text="Tel. for Reference")
    financial_guarantor = serializers.CharField(max_length=300, required=False, default="", allow_blank=True, help_text="Financial Guarantor")

    # Current Address in China
    china_address = serializers.CharField(max_length=500, required=False, default="", allow_blank=True, help_text="Present address in China")

    # Studied in China
    studied_in_china = serializers.CharField(max_length=10, required=False, default="□", allow_blank=True, help_text="Yes ☑ or No □")
    studied_in_china_institution = serializers.CharField(max_length=300, required=False, default="", allow_blank=True, help_text="Chinese Institutions studied")
    studied_in_china_duration = serializers.CharField(max_length=100, required=False, default="", allow_blank=True, help_text="Duration of former study in China")

    # Education Background (up to 3 entries)
    edu_institution_1 = serializers.CharField(max_length=300, required=False, default="", allow_blank=True, help_text="Education institution 1")
    edu_major_1 = serializers.CharField(max_length=200, required=False, default="", allow_blank=True, help_text="Major 1")
    edu_years_1 = serializers.CharField(max_length=100, required=False, default="", allow_blank=True, help_text="Years attended 1")
    edu_certificates_1 = serializers.CharField(max_length=200, required=False, default="", allow_blank=True, help_text="Certificates 1")

    edu_institution_2 = serializers.CharField(max_length=300, required=False, default="", allow_blank=True, help_text="Education institution 2")
    edu_major_2 = serializers.CharField(max_length=200, required=False, default="", allow_blank=True, help_text="Major 2")
    edu_years_2 = serializers.CharField(max_length=100, required=False, default="", allow_blank=True, help_text="Years attended 2")
    edu_certificates_2 = serializers.CharField(max_length=200, required=False, default="", allow_blank=True, help_text="Certificates 2")

    edu_institution_3 = serializers.CharField(max_length=300, required=False, default="", allow_blank=True, help_text="Education institution 3")
    edu_major_3 = serializers.CharField(max_length=200, required=False, default="", allow_blank=True, help_text="Major 3")
    edu_years_3 = serializers.CharField(max_length=100, required=False, default="", allow_blank=True, help_text="Years attended 3")
    edu_certificates_3 = serializers.CharField(max_length=200, required=False, default="", allow_blank=True, help_text="Certificates 3")

    # Work Experience
    employer = serializers.CharField(max_length=300, required=False, default="", allow_blank=True, help_text="Employer")
    employer_location = serializers.CharField(max_length=200, required=False, default="", allow_blank=True, help_text="Location of employer")
    position = serializers.CharField(max_length=200, required=False, default="", allow_blank=True, help_text="Position")
    employment_period = serializers.CharField(max_length=100, required=False, default="", allow_blank=True, help_text="Period of Employment")

    # Language
    hsk_level = serializers.CharField(max_length=100, required=False, default="", allow_blank=True, help_text="HSK Level or certificate")
    chinese_learning_institution = serializers.CharField(max_length=300, required=False, default="", allow_blank=True, help_text="Chinese learning institution")
    chinese_learning_years = serializers.CharField(max_length=100, required=False, default="", allow_blank=True, help_text="Chinese learning years")

    # Application Info
    program = serializers.CharField(max_length=100, required=False, default="", allow_blank=True, help_text="Program: undergraduate/graduate/phd/general_scholar")
    specialty_direction = serializers.CharField(max_length=300, required=False, default="", allow_blank=True, help_text="Specialty and Direction of Research")
    intended_study_length = serializers.CharField(max_length=100, required=False, default="", allow_blank=True, help_text="Intended Length of Study")
    financial_resource = serializers.CharField(max_length=100, required=False, default="", allow_blank=True, help_text="Financial Resource: government/self_supported")

    # Referee
    referee_name = serializers.CharField(max_length=200, required=False, default="", allow_blank=True, help_text="Referee Full Name")
    referee_email = serializers.CharField(max_length=200, required=False, default="", allow_blank=True, help_text="Referee Email")
    referee_tel = serializers.CharField(max_length=50, required=False, default="", allow_blank=True, help_text="Referee Tel")
    referee_fax = serializers.CharField(max_length=50, required=False, default="", allow_blank=True, help_text="Referee Fax")
