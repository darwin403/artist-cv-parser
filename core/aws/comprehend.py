import re

import boto3

from config import AWS_ACCESS_KEY_ID, AWS_REGION_NAME, AWS_SECRET_ACCESS_KEY

comprehend = boto3.client(
    "comprehend",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION_NAME,
)


def ExtractName(text):
    response = comprehend.detect_entities(Text=text, LanguageCode="en")
    entities = response["Entities"]

    if not entities:
        return None

    for i in entities:
        if i["Type"] == "PERSON":
            return i["Text"].title()


def ExtractBirthday(text):
    regex = r"(?:19|20)\d{2}"
    dates = re.findall(regex, text)

    if not dates:
        return None

    dates.sort()

    if len(dates) == 1:
        return dates[0]

    # not prodigy lol
    if int(dates[1]) - int(dates[0]) >= 18:
        return dates[0]


class ExtractExhibition:
    def __init__(self, **config):
        self.delimeter = config.get("delimeter") or ","
        self.maxDelimeters = config.get("maxDelimeters") or 3

    def clean(self):
        self.year = self.year.strip()
        self.text = [
            i.strip() for i in self.text.split(self.delimeter, self.maxDelimeters - 1)
        ]

    def has_location(self, text):
        fooling_ml_text = "{location}".format(location=", ".join(text))
        response = comprehend.detect_entities(Text=fooling_ml_text, LanguageCode="en")
        entities = response["Entities"]

        # print("Location Entities:", entities)

        if not entities:
            return False

        for i in entities:
            if not list(set(i["Text"].split(" ")) & set(text[-1].split(" "))):
                continue
            if i["Type"] in ["LOCATION", "ORGANIZATION"]:
                return True

        return False

    def is_other(self, text):
        fooling_ml_text = "{text}".format(text=text)
        response = comprehend.detect_entities(Text=fooling_ml_text, LanguageCode="en")
        entities = response["Entities"]

        if not entities:
            return True

        for i in entities:
            if i["Type"] in ["DATE", "OTHER"]:
                return True

        return False

    def is_title(self, text):
        # first check
        fooling_ml_text = "Title: {title} ({year})".format(
            year=self.year, title=text[0]
        )
        response = comprehend.detect_entities(Text=fooling_ml_text, LanguageCode="en")
        entities = response["Entities"]

        # print ('Title Entities:', entities)

        if not entities:
            return False

        for i in entities:
            intersection = list(set(i["Text"].split(" ")) & set(text[0].split(" ")))
            # print("INTERSECTION:", intersection, text[0], i)
            if not intersection:
                continue
            if i["Type"] in ["EVENT", "TITLE"]:
                return True

        # second check
        fooling_ml_text = "Title: {title} ({year}), {location}".format(
            year=self.year, title=text[0], location=", ".join(text[1:])
        )
        response = comprehend.detect_entities(Text=fooling_ml_text, LanguageCode="en")
        entities = response["Entities"]

        if not entities:
            return False

        for i in entities:
            if not list(set(i["Text"].split(" ")) & set(text[0].split(" "))):
                continue
            if i["Type"] in ["EVENT", "TITLE"]:
                return True

        return False

    def process(self, year, text):
        self.year = year
        self.text = text

        self.clean()

        # title check
        if self.is_title(self.text):
            return self.text[0]

        # has location check
        if len(self.text) >= 2:
            if not self.has_location(self.text):
                return False
        else:
            if self.has_location(self.text):
                return False

        # blind title extraction
        if len(self.text) >= self.maxDelimeters:
            return self.text[0]
        else:
            if self.has_location(self.text[:1]):
                return False
            if self.is_other(self.text[:1]):
                return False

        return None


if __name__ == "__main__":
    exhibition = ExtractExhibition()
    title = exhibition.process(
        year="2014",
        text="The Good Son; Michael Zavros, A survey of works on paper, Gold Coast City Art",
    )
    print(title)

    birthday = ExtractBirthday(
        """Australian Galleries
    L E W IS M I LLE R
    Born 1959, Melbourne, Australia
    1977-79 Studied painting at Victorian"""
    )
    print(birthday)

    name = ExtractName("I love movies. Brad Pitt is an actor")
    print(name)
