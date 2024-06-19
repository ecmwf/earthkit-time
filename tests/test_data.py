import os

import pytest

from earthkit.time.data import ResourceType, find_resource


def test_find_resource(
    monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempPathFactory
):
    # Packaged resources only
    assert find_resource("sequences/ecmwf-mon-thu.yaml")[0] == ResourceType.PACKAGED
    assert find_resource("sequences/nonexistent")[0] == ResourceType.NOTFOUND

    custom = tmp_path_factory.mktemp("custom")
    custom_foo = custom / "foo.txt"
    custom_foo.write_text("Hello!")
    custom_seq = custom / "ecmwf-mon-thu.yaml"
    custom_seq.write_text("type: weekly\ndays: [0, 3]\n")

    # Resource by path
    assert find_resource("sequences/test-hello", path=str(custom_foo)) == (
        ResourceType.FILE,
        str(custom_foo),
    )

    # Path overrides packaged
    assert find_resource("sequences/ecmwf-mon-thu.yaml", path=str(custom_foo)) == (
        ResourceType.FILE,
        str(custom_foo),
    )

    # Non-existent path does not override
    assert (
        find_resource(
            "sequences/ecmwf-mon-thu.yaml", path=str(custom / "nonexistent.txt")
        )[0]
        == ResourceType.PACKAGED
    )

    # Resource by env file
    with monkeypatch.context() as m:
        m.setenv("TEST_RES_FILE", str(custom_foo))
        assert find_resource("sequences/test-hello", env_file="TEST_RES_FILE") == (
            ResourceType.FILE,
            str(custom_foo),
        )

    # Non-existent env file
    with monkeypatch.context() as m:
        m.setenv("TEST_RES_FILE", str(custom / "nonexistent.txt"))
        assert (
            find_resource("sequences/test-hello", env_file="TEST_RES_FILE")[0]
            == ResourceType.NOTFOUND
        )

    # Env file overrides packaged
    with monkeypatch.context() as m:
        m.setenv("TEST_RES_FILE", str(custom_seq))
        assert find_resource(
            "sequences/ecmwf-mon-thu.yaml", env_file="TEST_RES_FILE"
        ) == (
            ResourceType.FILE,
            str(custom_seq),
        )

    # Non-existent env file does not override
    with monkeypatch.context() as m:
        m.setenv("TEST_RES_FILE", str(custom / "nonexistent.txt"))
        assert (
            find_resource("sequences/ecmwf-mon-thu.yaml", env_file="TEST_RES_FILE")[0]
            == ResourceType.PACKAGED
        )

    other = tmp_path_factory.mktemp("other")
    other_foo = other / "foo.txt"
    other_foo.write_text("Hi there!")
    other_bar = other / "bar.txt"
    other_bar.write_text("Testing")

    # Path overrides env file
    with monkeypatch.context() as m:
        m.setenv("TEST_RES_FILE", str(custom_foo))
        assert find_resource(
            "sequences/test-hello", path=str(other_foo), env_file="TEST_RES_FILE"
        ) == (
            ResourceType.FILE,
            str(other_foo),
        )

    # Resource by env path, with precedence
    with monkeypatch.context() as m:
        m.setenv("TEST_RES_DIR", os.pathsep.join([str(other), str(custom)]))
        assert find_resource("sequences/foo.txt", env_path="TEST_RES_DIR") == (
            ResourceType.FILE,
            str(other_foo),
        )

    # Resource by env path, not present in first dir
    with monkeypatch.context() as m:
        m.setenv("TEST_RES_DIR", os.pathsep.join([str(custom), str(other)]))
        assert find_resource("sequences/bar.txt", env_path="TEST_RES_DIR") == (
            ResourceType.FILE,
            str(other_bar),
        )

    # Resource by env path, non-existent
    with monkeypatch.context() as m:
        m.setenv("TEST_RES_DIR", os.pathsep.join([str(custom), str(other)]))
        assert (
            find_resource("sequences/nonexistent", env_path="TEST_RES_DIR")[0]
            == ResourceType.NOTFOUND
        )

    # Env path overrides packaged
    with monkeypatch.context() as m:
        m.setenv("TEST_RES_DIR", os.pathsep.join([str(other), str(custom)]))
        assert find_resource(
            "sequences/ecmwf-mon-thu.yaml", env_path="TEST_RES_DIR"
        ) == (
            ResourceType.FILE,
            str(custom_seq),
        )

    # Non-existent env path does not override
    with monkeypatch.context() as m:
        m.setenv("TEST_RES_DIR", os.pathsep.join([str(other / "nonexistent")]))
        assert (
            find_resource("sequences/ecmwf-mon-thu.yaml", env_path="TEST_RES_DIR")[0]
            == ResourceType.PACKAGED
        )

    # Env file overrides env path
    with monkeypatch.context() as m:
        m.setenv("TEST_RES_FILE", str(other_bar))
        m.setenv("TEST_RES_DIR", os.pathsep.join([str(other), str(custom)]))
        assert find_resource(
            "sequences/foo.txt", env_file="TEST_RES_FILE", env_path="TEST_RES_DIR"
        ) == (
            ResourceType.FILE,
            str(other_bar),
        )

    # Path overrides env path
    with monkeypatch.context() as m:
        m.setenv("TEST_RES_DIR", os.pathsep.join([str(other), str(custom)]))
        assert find_resource(
            "sequences/foo.txt", path=str(other_bar), env_path="TEST_RES_DIR"
        ) == (
            ResourceType.FILE,
            str(other_bar),
        )
