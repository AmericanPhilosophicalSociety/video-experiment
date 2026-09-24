"""
Scripts for communicating with the APS digital library
"""

import json
import logging
import os
import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


logger = logging.getLogger(__name__)


class DiglibAPI:
    """API for interacting with the APS Digital Library"""

    base_url = "https://diglib.amphilsoc.org/"

    def __init__(self):
        try:
            self.user = settings.APS_DIGLIB_USERNAME
        except AttributeError:
            raise ImproperlyConfigured(
                "APS_DIGLIB_USERNAME is required for Diglib API"
            )
        try:
            self.password = settings.APS_DIGLIB_PASSWORD
        except AttributeError:
            raise ImproperlyConfigured(
                "APS_DIGLIB_PASSWORD is required for Diglib API"
            )

        self.session = requests.Session()
        self.session.auth = (self.user, self.password)

        # add user agent to the headers
        self.session.headers.update({"User-Agent": "APSMeetingsVideos/0.1.0"})

        tech_contact = getattr(settings, "TECHNICAL_CONTACT", None)
        if tech_contact:
            self.session.headers.update({"From": tech_contact}) 
 
    def get_pdf_metadata(self, node_id):
        """Make request to APS Digital Library to retrieve basic metadata"""
        api_url = self.base_url + "admin/meetings_programs/"
        url = api_url + str(node_id)
        r = self.session.get(url).json()[0]
        mid = r.pop('mid')
        return r, mid

    def retrieve_original_filepath(self, mid):
        """Make request to the APS Digital Library to retrieve original file filepath"""
        api_url = self.base_url + 'media/'
        url = api_url + str(mid) + '?_format=json'
        r = self.session.get(url).json()
        pdf_path = r['field_media_document']['0']['url']
        return pdf_path


    def retrieve_thumbnail_path(self, node_id):
        api_url = self.base_url + 'admin/thumbnail_paths/'
        url = api_url + str(node_id)
        r = self.session.get(url).json()

        for result in r:
            thumbnail_path = result['thumbnail__target_id']
            if 'generic' not in thumbnail_path:
                break
        # if no good thumbnail found
        else:
            logger.warn(f"No good thumbnail found for {node_id}.")

        # format thumbnail path
        thumbnail_path = self.base_url + thumbnail_path
        return thumbnail_path

    def generate_iiif_data(self, node_id, metadata, pdf_path, thumbnail_path):
        doc_id = settings.BASE_URL + os.path.join(settings.STATIC_URL, 'manifests', str(node_id))
        iiif_data = {
            "@context": "https://iiif.io/api/presentation/2/context.json",
            "@id": doc_id,
            "@type": "sc:Manifest",
            "label": metadata["title"]
            "thumbnail": {
                "@id": thumbnail_path,
                "@type": "dctypes:Image",
            },
            "mediaSequences": [
                {
                    "@id": doc_id + '/s0'
                    "@type": "ixif:MediaSequence",
                    "label": "XSequence 0",
                    "elements": [
                        "@id": pdf_path,
                        "@type": "foaf:Document",
                        "format": "application/pdf",
                        "label": metadata["title"],
                        "metadata": [
                            "label" "pages",
                            "value": metadata['field_extent'].replace('p.', '')
                        ],
                        "thumbnail": thumbnail_path,
                    ]
                },
            ]
        }
        prepped_metadata = []
        # check for metadata
        def format_metadata(field, value):
            return {
                "label": field,
                "value": value
            }
        prepped_metadata.append(format_metadata("Title", metadata["title"]))
        if metadata['field_linked_agent'] != "":
            agent = metadata['field_linked_agent'].split('|')[0]
            prepped_metadata.append(format_metadata("Creator", agent))
        if metadata['field_resource_type'] != "":
            resource_type = metadata['field_resource_type']
            prepped_metadata.append(format_metadata("Resource Type", resource_type))
        if metadata["field_subject"] != '':
             subject = metadata['field_subject'].split('|')[0]
             prepped_metadata.append(format_metadata("Subject", subject))
        if metadata["field_genre"] != '':
             genre = metadata['field_genre'].split('|')[0]
             prepped_metadata.append(format_metadata("Genre", subject))
        if metadata["field_note"] != '':
             note = metadata['field_note'].split('|')[0]
             prepped_metadata.append(format_metadata("Note", note))
        if metadata["field_extent"] != '':
             extent = metadata['field_extent'].split('|')[0]
             prepped_metadata.append(format_metadata("Extent", extent))

        iiif_data.update("metadata": prepped_metadata)

        return iiif_data

    def make_iiif_manifest(self, node_id):
        """Generate but don't save IIIF manifest"""
        metadata, mid = self.get_pdf_metadata(node_id)
        pdf_path = self.retrieve_original_filepath(mid)
        thumbnail_path = self.retrieve_thumbnail_path(node_id)
        iiif_data = generate_iiif_data(node_id, metadata, pdf_path, thumbnail_path)
        return iiif_data

    def generate_and_save_iiif_manifest(node_id):
        iiif_data = self.make_iiif_manifest(node_id)
        filepath = os.path.join(settings.STATIC_URL, 'manifests', str(node_id))
        with open(filepath, 'w') as f:
            json.dump(iiif_data, f)
