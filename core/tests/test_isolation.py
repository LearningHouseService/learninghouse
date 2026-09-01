"""Direct evidence that two tests in the same session can use two different
brains directories. The rest of the suite relies on this implicitly - every
test using `isolated_client` gets its own directory, and none of them
collide - but this test makes the claim explicit within a single test
function, where no test-ordering assumption is needed.

`service_settings()` is a process-wide `lru_cache` with no arguments: what
was de-globalized is *how* settings are read, not the fact that there is one
cache slot per process. Two isolated_client fixtures
cannot be requested from the same test, so this test reproduces
isolated_client's own mechanism - point the config directory env var at a
fresh directory and clear the cache - twice in sequence, and shows that
brain data created under the first directory is invisible once the second
is active.
"""

import os
import shutil
import tempfile


class TestTwoBrainsDirectoriesInOneProcess:
    def test_brain_data_does_not_leak_across_directories(self):
        from learninghouse.core.settings import service_settings

        config_directory_env = "LEARNINGHOUSE_CONFIG_DIRECTORY"
        previous = os.environ.get(config_directory_env)
        directories = [
            tempfile.mkdtemp(prefix="learninghouse-isolation-a-"),
            tempfile.mkdtemp(prefix="learninghouse-isolation-b-"),
        ]

        try:
            os.environ[config_directory_env] = directories[0]
            service_settings.cache_clear()

            from learninghouse.models.brain import BrainConfiguration
            from learninghouse.services.brain import BrainConfigurationService

            configuration_a = BrainConfiguration.model_validate(
                {
                    "name": "only-in-a",
                    "estimator": {"typed": "classifier"},
                }
            )
            BrainConfigurationService.create(configuration_a)
            assert BrainConfiguration.json_config_file_exists("only-in-a")

            os.environ[config_directory_env] = directories[1]
            service_settings.cache_clear()

            # Same process, different directory: the brain created above is
            # invisible here, proving the two directories are genuinely
            # independent rather than sharing state through some leftover
            # process-wide cache.
            assert not BrainConfiguration.json_config_file_exists("only-in-a")
        finally:
            if previous is None:
                os.environ.pop(config_directory_env, None)
            else:
                os.environ[config_directory_env] = previous
            service_settings.cache_clear()
            for directory in directories:
                shutil.rmtree(directory, ignore_errors=True)
