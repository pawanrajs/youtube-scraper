from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
import json
import sys

class YouScraper:
    
    def __init__(self, config_path="config.json"):

        """
        Sets up the Youtube API client.
        Takes path of a json configuration file that has information: 
            Youtube API Key
            serviceName ('youtube' if not found in configfile)
            version ('v3' if not found in config file)
        """
        # First get the json from your config file
        # TODO: Error handling for the file
        # TODO: Error handling for creating the youtube service object
        with open(config_path, "r") as f:
            self.config = json.load(f)

        service_name = self.config.get("serviceName", "youtube")
        service_version = self.config.get("version", "v3")
        api_key = self.config.get("apiKey")
        
        self.youtube = build(service_name, service_version, developerKey=api_key)
        
        # Set Logging
        # self.logger = logging.getLogger()
        # self.logger.setLevel(logging.DEBUG)
        # logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)])


    def get_channel_info(self, channel_id, return_info=None):
        """
        Gets information about an individual channel (specified by channel id)
        Returns a dictionary object based on values specified by return_info
        return_info is a dictionary that has the "attributes" of the channel to return, from API
        If return_info is None (default) returns all information about the channel
        """
        
        # All Parts that can be retrieved using API Key
        channel_parts = {
            "brandingSettings": ["keywords"],
            "contentOwnerDetails": ["contentOwner", "timeLinked"],
            "snippet": ["title", "description", "customUrl", "publishedAt", "defaultLanguage", "country"],
            "statistics": ["viewCount", "commentCount", "subscriberCount", "videoCount", "hiddenSubscriberCount"],
            "status": ["privacyStatus", "isLinked", "longUploadsStatus", "madeForKids", "selfDeclaredMadeForKids"],
            "topicDetails": ["topicCategories"],
        }

        channel_info = {}
        
        # If return info is not passed, create a return info consisting of all attributes
        if not return_info:
            return_info = [info for lst in channel_parts.values() for info in lst]

        # Figure out what parts to get based on return_info
        parts = set()
        info_to_get = {}
        for info in return_info:
            for part in channel_parts.items():
                # print(part)
                if info in part[1]:
                    parts.add(part[0])
                    info_to_get.setdefault(part[0], []).append(info)   
                    break
        
        # DEBUG STATEMENTS
        # print("info_to_get: ", info_to_get)
        # print("parts: ", parts)

        try:
            channel_detail = self.youtube.channels().list(
                part=",".join(parts), id=channel_id).execute()['items'][0]
            for part, props in info_to_get.items():
                for prop in props:
                    if part == "brandingSettings":
                        channel_info[prop] = channel_detail[part]["channel"].get(prop)
                    else:
                        channel_info[prop] = channel_detail[part].get(prop)
        except HttpError as httpe:
            self._handle_exception(httpe)
        finally:
            self.youtube.close()

        return channel_info

    def search_channels(self, search_term, max_channels, **kwargs):
        """
        Provide API options as kwargs based on YT API
        - part will be "snippet" by default
        - type will be "channel" by default
        """

        # Update default parameters
        kwargs["part"] = "snippet"
        kwargs["type"] = "channel"
        kwargs["q"] = search_term
        kwargs["maxResults"] = min(max_channels, 50)

        search_collection = self.youtube.search()
        search_request = search_collection.list(**kwargs)

        total_channels = 0
        channel_list = []

        while max_channels > len(channel_list) and search_request is not None:
            try:
                response = search_request.execute()
            except HttpError as httpe:
                self._handle_exception(httpe)
                break
            finally:
                self.youtube.close()

            search_result = response['items']
            for channel in search_result:
                # Append channel to list
                channel_list.append(channel["snippet"])
                if len(channel_list) == max_channels:
                    break

                # Get Next Page
            search_request = search_collection.list_next(search_request, response)
            print(len(channel_list), " items in the list so far!")
        
        return channel_list
    
    def _handle_exception(ex):
        error_dict = json.loads(ex.content.decode('utf-8'))
        print("Error ({}) in calling Youtube API: {}".format(
            ex.resp.status, error_dict['error']['message']
        ))

