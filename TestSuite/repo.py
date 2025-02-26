import os
import shutil
from pathlib import Path
from typing import List, Optional

from TestSuite.conf_json import ConfJSON
from TestSuite.docker_native_image_config import DockerNativeImageConfiguration
from TestSuite.global_secrets import GlobalSecrets
from TestSuite.json_based import JSONBased
from TestSuite.pack import Pack

DEFAULT_MARKETPLACES = ["xsoar"]


class Repo:
    """A class that mocks a content repo

    Note:
        Do not include the `self` parameter in the ``Args`` section.

    Args:
        tmpdir: A Path to the root of the repo

    Attributes:
        path: A path to the content pack.
        secrets: Exception error code.
        packs: A list of created packs
    """

    def __init__(self, tmpdir: Path):
        self.packs: List[Pack] = list()
        self._tmpdir = tmpdir
        self._packs_path = tmpdir / "Packs"
        self._packs_path.mkdir()
        self.path = str(self._tmpdir)

        # Initiate ./Tests/ dir
        self._test_dir = tmpdir / "Tests"
        self._test_dir.mkdir()

        # Secrets
        self.secrets = GlobalSecrets(self._test_dir)
        self.secrets.write_secrets()
        self.global_secrets_path = self.secrets.path

        # Conf.json
        self.conf = ConfJSON(self._test_dir, "conf.json", "")
        self.conf.write_json()

        # docker native image config
        self.docker_native_image_config = DockerNativeImageConfiguration(self._test_dir)
        self.docker_native_image_config.write_native_image_config()

        self.content_descriptor = JSONBased(self._tmpdir, "content-descriptor", "")
        self.content_descriptor.write_json({})

        self.id_set = JSONBased(self._test_dir, "id_set", "")
        self.id_set.write_json(
            {
                "scripts": [],
                "playbooks": [],
                "integrations": [],
                "TestPlaybooks": [],
                "Classifiers": [],
                "Dashboards": [],
                "IncidentFields": [],
                "IncidentTypes": [],
                "IndicatorFields": [],
                "IndicatorTypes": [],
                "Layouts": [],
                "Reports": [],
                "Widgets": [],
                "Mappers": [],
                "GenericTypes": [],
                "GenericFields": [],
                "GenericModules": [],
                "GenericDefinitions": [],
                "Jobs": [],
                "Wizards": [],
            }
        )

    def __del__(self):
        shutil.rmtree(self.path, ignore_errors=True)

    def setup_one_pack(
        self, name, marketplaces: List[str] = DEFAULT_MARKETPLACES
    ) -> Pack:
        """Sets up a new pack in the repo, and includes one per each content entity.

        Args:
            name (string): Name of the desired pack.
            marketplaces (list): List of the marketplaces to setup the packs.

        Returns:
            Pack. The pack object created.

        """
        pack = self.create_pack(name)
        pack.pack_metadata.update({"marketplaces": marketplaces})

        script = pack.create_script(f"{name}_script")
        script.create_default_script()
        script.yml.update({"commonfields": {"id": f"{name}_script"}})
        script.yml.update({"name": f"{name}_script"})
        script.yml.update({"display": f"{name}_script"})

        integration = pack.create_integration(f"{name}_integration")
        integration.create_default_integration()
        integration.yml.update({"commonfields": {"id": f"{name}_integration"}})
        integration.yml.update({"name": f"{name}_integration"})
        integration.yml.update({"display": f"{name}_integration"})
        integration_content = integration.yml.read_dict()
        integration_content["script"]["commands"][0][
            "name"
        ] = f"command_{name}_integration"
        integration.yml.write_dict(integration_content)

        classifier = pack.create_classifier(f"{name}_classifier")
        classifier.write_json({"id": f"{name} - classifier"})
        classifier.update({"name": f"{name} - classifier"})
        classifier.update({"transformer": {}})
        classifier.update({"keyTypeMap": {}})
        classifier.update({"type": "classification"})

        layout = pack.create_layout(f"{name}_layout")
        layout.write_json({"id": f"{name} - layout"})
        layout.update({"name": f"{name} - layout"})
        layout.update({"kind": ""})

        layoutcontainer = pack.create_layoutcontainer(f"{name}_layoutcontainer")
        layoutcontainer.write_json({"id": f"{name} - layoutcontainer"})
        layoutcontainer.update({"name": f"{name} - layoutscontainer"})
        layoutcontainer.update({"group": "incident"})
        layoutcontainer.update({"detailsV2": {}})

        mapper = pack.create_mapper(f"{name}_mapper")
        mapper.write_json({"id": f"{name} - mapper"})
        mapper.update({"name": f"{name} - mapper"})
        mapper.update({"mapping": {}})
        mapper.update(
            {"type": "mapping-incoming"}
        )  # can also be mapping-outgoing, but this is the more common usage

        incident_type = pack.create_incident_type(f"{name}_incident-type")
        incident_type.write_json({"id": f"{name} - incident_type"})
        incident_type.update({"name": f"{name} - incident_type"})
        incident_type.update({"preProcessingScript": ""})
        incident_type.update({"color": "test"})
        incident_type.update({"hours": 0})
        incident_type.update({"days": 3})
        incident_type.update({"weeks": 1})

        incident_field = pack.create_incident_field(f"{name}_incident-field")
        incident_field.write_json({"id": f"incident_{name} - incident_field"})
        incident_field.update({"name": f"incident_{name} - incident_field"})
        incident_field.update({"cliName": f"cliName-{name}"})
        incident_field.update({"type": "multiSelect"})
        incident_field.update({"associatedToAll": True})

        indicator_type = pack.create_indicator_type(f"{name}_indicator-type")
        indicator_type.write_json({"id": f"{name} - indicator_type"})
        indicator_type.update({"details": f"{name} - indicator_type"})
        indicator_type.update({"regex": ""})

        indicator_field = pack.create_indicator_field(f"{name}_indicator-field")
        indicator_field.write_json({"id": f"indicator_{name} - indicator_field"})
        indicator_field.update({"name": f"indicator_{name} - indicator_field"})
        indicator_field.update({"cliName": f"cliName-{name}"})
        indicator_field.update({"type": "multiSelect"})
        indicator_field.update({"associatedToAll": True})

        dashboard = pack.create_dashboard(f"{name}_dashboard")
        dashboard.write_json({"id": f"{name} - dashboard"})
        dashboard.update({"name": f"{name} - dashboard"})
        dashboard.update({"layout": ""})

        report = pack.create_report(f"{name}_report")
        report.write_json({"id": f"{name} - report"})
        report.update({"name": f"{name} - report"})
        report.update({"orientation": ""})

        widget = pack.create_widget(f"{name}_widget")
        widget.write_json({"id": f"{name} - widget"})
        widget.update({"name": f"{name} - widget"})
        widget.update({"widgetType": ""})

        pack.create_wizard(f"{name}_wizard")

        list_item = pack.create_list(f"{name}_list")
        list_item.write_json({"id": f"{name} - list"})
        list_item.update({"name": f"{name} - list"})
        list_item.update({"allRead": "True"})
        list_item.update({"truncated": "True"})
        list_item.update({"type": "plain_text"})

        playbook = pack.create_playbook(f"{name}_playbook")
        playbook.create_default_playbook()
        playbook.yml.update({"id": f"{name}_playbook"})
        playbook.yml.update({"name": f"{name}_playbook"})

        test_playbook = pack.create_test_playbook(f"{name}_integration_test_playbook")
        test_playbook.create_default_playbook()
        test_playbook.yml.update({"id": f"{name}_integration_test_playbook"})
        test_playbook.yml.update({"name": f"{name}_integration_test_playbook"})
        integration.yml.update({"tests": [f"{name}_integration_test_playbook"]})

        test_playbook = pack.create_test_playbook(f"{name}_script_test_playbook")
        test_playbook.create_default_playbook()
        test_playbook.yml.update({"id": f"{name}_script_test_playbook"})
        test_playbook.yml.update({"name": f"{name}_script_test_playbook"})
        script.yml.update({"tests": [f"{name}_script_test_playbook"]})

        generic_type = pack.create_generic_type(f"{name}_generic-type")
        generic_type.write_json({"id": f"{name} - _generic_type"})
        generic_type.update({"name": f"{name} - _generic_type"})
        generic_type.update({"definitionId": "definitionId"})
        generic_type.update({"color": "test"})

        generic_field = pack.create_generic_field(f"{name}_generic-field")
        generic_field.write_json({"id": f"generic_{name} - generic_field"})
        generic_field.update({"name": f"generic_{name} - generic_field"})
        generic_field.update({"definitionId": "definitionId"})

        generic_module = pack.create_generic_module(f"{name}_generic-module")
        generic_module.write_json({"id": f"generic_{name} - generic_module"})
        generic_module.update({"name": f"generic_{name} - generic_module"})
        generic_module.update({"views": [{"name": "name"}]})
        generic_module.update({"definitionIds": ["definitionId"]})

        generic_definition = pack.create_generic_definition(
            f"{name}_generic-definition"
        )
        generic_definition.write_json({"id": f"generic_{name} - generic_definition"})
        generic_definition.update({"name": f"generic_{name} - generic_definition"})
        generic_definition.update({"auditable": False})

        pack.create_job(is_feed=False, name=name)
        pack.create_job(is_feed=True, name=f"{name}_all_feeds")

        if "marketplacev2" in marketplaces:
            pack.create_parsing_rule(
                f"{name}_parsingrule",
                {"id": "parsing_rule_id", "rules": "", "name": "parsing_rule_name"},
            )
            pack.create_modeling_rule(
                f"{name}_modelingrule",
                {"id": "modeling_rule_id", "rules": "", "name": "modeling_rule_name"},
            )
            pack.create_correlation_rule(
                f"{name}_correlationrule",
                {
                    "global_rule_id": "correlation_rule_id",
                    "name": "correlation_rule_name",
                    "alert_category": "",
                },
            )
            pack.create_xsiam_dashboard(
                f"{name}_xsiamdashboard",
                {
                    "dashboards_data": [
                        {
                            "global_id": "xsiam_dashboard_id",
                            "name": "xsiam_dashboard_name",
                        }
                    ]
                },
            )
            pack.create_xsiam_report(
                f"{name}_xsiamreport",
                {
                    "templates_data": [
                        {"global_id": "xsiam_report_id", "name": "xsiam_report_name"}
                    ]
                },
            )
            pack.create_trigger(
                f"{name}_trigger",
                {"trigger_id": "trigger_id", "trigger_name": "trigger_name"},
            )
            print("parsing done")
        return pack

    def setup_content_repo(
        self, number_of_packs, marketplaces: List[str] = DEFAULT_MARKETPLACES
    ):
        """Creates a fully constructed content repository, where packs names will pack_<index>.

        Args:
            number_of_packs (int): Amount of packs to be created in the repo.
            marketplaces (List[str]): List of the marketplaces to setup the packs.

        """
        for i in range(number_of_packs):
            self.setup_one_pack(f"pack_{i}", marketplaces)

    def create_pack(self, name: Optional[str] = None):
        if name is None:
            name = f"pack_{len(self.packs)}"
        pack = Pack(self._packs_path, name, repo=self)
        self.packs.append(pack)
        return pack

    def working_dir(self):
        return self.path

    def make_dir(self, dir_name: str = ""):
        if not dir_name:
            dir_name = "NewDir"
        dir_path = os.path.join(self.path, dir_name)
        os.mkdir(dir_path)
        return dir_path

    def make_file(self, file_name: str, file_content: str):
        file_path = os.path.join(self.path, file_name)
        with open(file_path, "w") as f:
            f.write(file_content)
