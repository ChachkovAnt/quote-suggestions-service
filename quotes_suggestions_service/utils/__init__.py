from .validators.spacy_validator import NameValidator
from .enums import Localization


NAME_VALIDATORS_MAPPING = {
    Localization.ENGLISH: NameValidator(Localization.ENGLISH),
}
