from xml.etree import ElementTree as ET

from pydantic import BaseModel


class ShiplistTemplate(BaseModel):
    batch_load_dataset: str = "HCLUSER.POC.TMP.BATCH.LOADLIB"
    online_load_dataset: str = "HCLUSER.POC.TMP.ONLINE.CICSLIB"
    batch_resources: set[str]
    online_resources: set[str]

    def _get_batch_container(self) -> str:
        if not self.batch_resources:
            return ""

        batch_resources = "\n".join(
            f"""<resource name="{resource}" type="PDSMember"/>"""
            for resource in self.batch_resources
        )
        return f"""<container name="{self.batch_load_dataset}" type="PDS" deployType="LOADLIB">
            {batch_resources}
        </container>
        """

    def _get_online_container(self) -> str:
        if not self.online_resources:
            return ""

        online_resources = "\n".join(
            f"""<resource name="{resource}" type="PDSMember"/>"""
            for resource in self.online_resources
        )
        return f"""<container name="{self.online_load_dataset}" type="PDS" deployType="CICS LOAD">
            {online_resources}
        </container>
        """

    def get_shiplist(self) -> str:
        raw_xml = f"""<manifest type="MANIFEST_SHIPLIST">
            {self._get_batch_container()}
            {self._get_online_container()}
        </manifest>"""

        root = ET.fromstring(raw_xml)
        ET.indent(root, space="    ", level=0)
        formatted_xml = ET.tostring(root, encoding="unicode")
        return f'<?xml version="1.0" encoding="CP037"?>\n{formatted_xml}'
