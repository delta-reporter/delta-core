import re
import datetime
from logzero import logger


class SmartLinks(object):
    """
    Class to manage Smart Links logic
    """

    def get_smart_links_for_test(self, smart_links, environment, test, test_data):
        """
        Smart links processing for tests
        """

        data = None
        if smart_links:
            data = self.generate_payload(smart_links, environment, test, test_data)

        return data

    def get_smart_links_for_test_run(
        self, smart_links, environment, test_run, test_run_data
    ):
        """
        Smart links processing for test runs
        """

        data = None
        if smart_links:
            data = self.generate_payload(
                smart_links, environment, test_run, test_run_data
            )

        return data

    def format_link(self, entity, entity_data, link):
        """
        Format of the link with data from the entity
        """
        try:
            if entity_data:
                smart_link = link.format(**entity, **entity_data)
            else:
                smart_link = link.format(**entity)
        except Exception:
            logger.exception("The SmartLink couldn't be processed")
            logger.info(Exception)

        return smart_link

    def apply_datetime_format(self, entity, datetime_format):
        """
        Application of the date format requested by user
        """

        if (
            entity.get("start_datetime")
            and type(entity.get("start_datetime")) == datetime.datetime
        ):
            entity["start_datetime"] = entity.get("start_datetime").strftime(
                datetime_format
            )
            if entity.get("end_datetime"):
                entity["end_datetime"] = entity.get("end_datetime").strftime(
                    datetime_format
                )

        return entity

    def generate_payload(self, smart_links, environment, entity, entity_data):
        """
        Payload generation to be returned back
        """
        data = []
        for sl in smart_links:
            try:
                if sl.get("filtered"):
                    if re.match(sl.get("environment"), environment):
                        entity = self.apply_datetime_format(
                            entity, sl.get("datetime_format")
                        )
                        link = self.format_link(
                            entity, entity_data, sl.get("smart_link")
                        )
                        data.append(
                            {
                                "smart_link_id": sl.get("id"),
                                "project_id": sl.get("project_id"),
                                "environment": sl.get("environment"),
                                "smart_link": link,
                                "label": sl.get("label"),
                                "color": sl.get("color"),
                            }
                        )
                else:
                    entity = self.apply_datetime_format(
                        entity, sl.get("datetime_format")
                    )

                    link = self.format_link(entity, entity_data, sl.get("smart_link"))
                    data.append(
                        {
                            "smart_link_id": sl.get("id"),
                            "project_id": sl.get("project_id"),
                            "environment": sl.get("environment"),
                            "smart_link": link,
                            "label": sl.get("label"),
                            "color": sl.get("color"),
                        }
                    )
            except Exception:
                logger.exception("The SmartLink couldn't be processed")
                logger.info(Exception)

            if not len(data):
                data = None

        return data
