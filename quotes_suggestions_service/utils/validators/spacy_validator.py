import en_core_web_sm

from quotes_suggestions_service.utils.enums import Localization

from .enums import SpacyTags


class NameValidator:

    localization = None
    _instances = []
    _initialized = False

    def __new__(cls, localization: Localization):
        localizations = (instance.localization for instance in cls._instances)

        if localization in localizations:
            instance = cls._get_localized_instance(localization)
        else:
            instance = super(NameValidator, cls).__new__(cls)
            instance._initialized = False
            cls._instances.append(instance)

        return instance

    def __init__(self, localization: Localization):
        if self._initialized:
            return

        self.localization = localization
        self.nlp = self._get_localized_nlp()

    def is_person(self, phrase: str):
        tagged_result = self.nlp(phrase)

        try:
            is_person = next(
                SpacyTags(tag.label_) == SpacyTags.PERSON
                for tag in tagged_result.ents) \
                if len(tagged_result.ents) \
                else False
        except ValueError:
            is_person = False

        return is_person

    @classmethod
    def _get_localized_instance(cls, localization: Localization):
        return next(
            instance
            for instance in cls._instances
            if instance.localization == localization)

    def _get_localized_nlp(self):
        if self.localization == Localization.ENGLISH:
            return en_core_web_sm.load()
        else:
            raise NotImplemented(f'Localization {self.localization.value} is not supported')
