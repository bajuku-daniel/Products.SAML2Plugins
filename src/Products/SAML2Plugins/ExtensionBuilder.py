from xml.etree.ElementTree import Element, SubElement, tostring
from saml2.samlp import Extensions

class DummyExtension:
    """
    Wrapper class for XML elements to make them compatible with PySAML2 extensions.

    This class provides the necessary methods `become_child_element_of` and `to_string`,
    which are required by PySAML2's serialization logic for SAML extension elements.
    """

    def __init__(self, element):
        """
        Initialize the DummyExtension.

        Args:
            element (xml.etree.ElementTree.Element): The XML element to wrap.
        """
        self.element = element

    def become_child_element_of(self, parent):
        """
        Attach the wrapped element as a child to the given parent element.

        Args:
            parent (xml.etree.ElementTree.Element): The parent XML element.
        """
        parent.append(self.element)

    def to_string(self):
        """
        Serialize the wrapped XML element to a Unicode string.

        Returns:
            str: The XML element as string.
        """
        return tostring(self.element, encoding="unicode")


class ExtensionBuilder:
    """
    Builder class for creating SAML2 AuthnRequest extensions, specifically for
    BundID, BayernID, Elster, or similar eGovernment SAML systems.

    The extensions are dynamically built based on configuration settings.
    """

    def __init__(self, config):
        """
        Initialize the ExtensionBuilder with a configuration dictionary.

        Args:
            config (dict): Configuration containing profile, version, requested attributes,
                           optional display information, and optional namespace prefixes.
        """
        self.profile = config.get("profile", "bundid")
        self.version = config.get("version", "2")
        self.requested_attributes = config.get("requested_attributes", [])
        self.display_information = config.get("display_information", {})

    def add_extensions(self, extensions_obj):
        """
        Add the constructed extension elements to the provided SAML Extensions object.

        Args:
            extensions_obj (saml2.samlp.Extensions): The Extensions object to which
                                                     the new extension elements will be appended.
        """
        akdb_ns = "https://www.akdb.de/request/2018/09"
        classic_ui_ns = "https://www.akdb.de/request/2018/09/classic-ui/v1"

        authn_elem = Element(f"{{{akdb_ns}}}AuthenticationRequest", Version=self.version)

        if self.requested_attributes:
            requested_attrs_elem = SubElement(authn_elem, f"{{{akdb_ns}}}RequestedAttributes")
            for attr in self.requested_attributes:
                attribs = {"Name": attr["name"]}
                attribs["RequiredAttribute"] = "true" if attr.get("required", False) else "false"
                SubElement(requested_attrs_elem, f"{{{akdb_ns}}}RequestedAttribute", attribs)

        if self.display_information:
            display_info_elem = SubElement(authn_elem, f"{{{akdb_ns}}}DisplayInformation")
            version_elem = SubElement(display_info_elem, f"{{{classic_ui_ns}}}Version")
            SubElement(version_elem, f"{{{classic_ui_ns}}}OrganizationDisplayName").text = self.display_information.get("organization_display_name", "")
            SubElement(version_elem, f"{{{classic_ui_ns}}}OnlineServiceId").text = self.display_information.get("online_service_id", "")

        dummy_extension = DummyExtension(authn_elem)
        extensions_obj.extension_elements.append(dummy_extension)
