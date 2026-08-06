from learninghouse import __version__, versions


class TestPackage:
    def test_version_is_reported(self):
        assert isinstance(__version__, str)
        assert __version__ != ""

    def test_versions_model_reports_service_version(self):
        assert versions.service == __version__

    def test_versions_model_reports_library_versions(self):
        assert "scikit-learn" in versions.libraries_versions
