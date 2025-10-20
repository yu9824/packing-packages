"""Tests for pack.yaml.constants module."""

import pytest

from packing_packages.pack.yaml.constants import PLATFORM_MAP


class TestPlatformMap:
    """Test PLATFORM_MAP constant."""

    def test_platform_map_structure(self):
        """Test PLATFORM_MAP structure."""
        assert isinstance(PLATFORM_MAP, dict)
        assert len(PLATFORM_MAP) > 0

    def test_platform_map_keys(self):
        """Test PLATFORM_MAP keys."""
        expected_keys = {
            "win-64",
            "win-32",
            "linux-64",
            "linux-aarch64",
            "linux-ppc64le",
            "linux-s390x",
            "osx-64",
            "osx-arm64",
        }
        assert set(PLATFORM_MAP.keys()) == expected_keys

    def test_platform_map_values(self):
        """Test PLATFORM_MAP values structure."""
        for platform, mapping in PLATFORM_MAP.items():
            assert isinstance(mapping, dict)
            assert "pypi" in mapping
            assert "conda" in mapping
            assert isinstance(mapping["pypi"], str)
            assert isinstance(mapping["conda"], str)

    def test_platform_map_win64(self):
        """Test PLATFORM_MAP for win-64."""
        win64 = PLATFORM_MAP["win-64"]
        assert win64["pypi"] == "win_amd64"
        assert win64["conda"] == "win-64"

    def test_platform_map_win32(self):
        """Test PLATFORM_MAP for win-32."""
        win32 = PLATFORM_MAP["win-32"]
        assert win32["pypi"] == "win32"
        assert win32["conda"] == "win-32"

    def test_platform_map_linux64(self):
        """Test PLATFORM_MAP for linux-64."""
        linux64 = PLATFORM_MAP["linux-64"]
        assert linux64["pypi"] == "manylinux2014_x86_64"
        assert linux64["conda"] == "linux-64"

    def test_platform_map_linux_aarch64(self):
        """Test PLATFORM_MAP for linux-aarch64."""
        linux_aarch64 = PLATFORM_MAP["linux-aarch64"]
        assert linux_aarch64["pypi"] == "manylinux2014_aarch64"
        assert linux_aarch64["conda"] == "linux-aarch64"

    def test_platform_map_linux_ppc64le(self):
        """Test PLATFORM_MAP for linux-ppc64le."""
        linux_ppc64le = PLATFORM_MAP["linux-ppc64le"]
        assert linux_ppc64le["pypi"] == "manylinux2014_ppc64le"
        assert linux_ppc64le["conda"] == "linux-ppc64le"

    def test_platform_map_linux_s390x(self):
        """Test PLATFORM_MAP for linux-s390x."""
        linux_s390x = PLATFORM_MAP["linux-s390x"]
        assert linux_s390x["pypi"] == "manylinux2014_s390x"
        assert linux_s390x["conda"] == "linux-s390x"

    def test_platform_map_osx64(self):
        """Test PLATFORM_MAP for osx-64."""
        osx64 = PLATFORM_MAP["osx-64"]
        assert osx64["pypi"] == "macosx_10_9_x86_64"
        assert osx64["conda"] == "osx-64"

    def test_platform_map_osx_arm64(self):
        """Test PLATFORM_MAP for osx-arm64."""
        osx_arm64 = PLATFORM_MAP["osx-arm64"]
        assert osx_arm64["pypi"] == "macosx_11_0_arm64"
        assert osx_arm64["conda"] == "osx-arm64"

    def test_platform_map_immutable(self):
        """Test that PLATFORM_MAP is immutable."""
        with pytest.raises(TypeError):
            PLATFORM_MAP["new-platform"] = {"pypi": "new", "conda": "new"}

    def test_platform_map_values_immutable(self):
        """Test that PLATFORM_MAP values are immutable."""
        with pytest.raises(TypeError):
            PLATFORM_MAP["win-64"]["pypi"] = "modified"

    def test_platform_map_consistency(self):
        """Test PLATFORM_MAP consistency."""
        for platform, mapping in PLATFORM_MAP.items():
            # Check that platform names are consistent
            assert platform in mapping["conda"]

            # Check that pypi and conda values are different
            assert mapping["pypi"] != mapping["conda"]

            # Check that values are not empty
            assert len(mapping["pypi"]) > 0
            assert len(mapping["conda"]) > 0

    def test_platform_map_documentation(self):
        """Test that PLATFORM_MAP has proper documentation."""
        # Check that the module has docstring
        from packing_packages.pack.yaml import constants

        assert constants.PLATFORM_MAP.__doc__ is not None
        assert len(constants.PLATFORM_MAP.__doc__) > 0
