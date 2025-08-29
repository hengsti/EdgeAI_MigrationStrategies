"""
Integration tests for the simulation module.
These tests cover various configurations and scenarios to ensure the simulation behaves as expected.
"""
import os
import tempfile
from itertools import product
import yaml
import pytest
import main as sim

TEST_CONFIG_PATH = os.path.join("test", "config_test.yaml")

@pytest.fixture(scope="module")
def base_config():
    """Load the base config once from test/test_config.yaml."""
    with open(TEST_CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def write_temp_config(config_data: dict) -> str:
    """Write config data to a temporary file and return its path."""
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
    yaml.dump(config_data, temp_file)
    temp_path = temp_file.name
    temp_file.close()
    return temp_path



@pytest.mark.parametrize("topology, strategy, offloading, loadbalancing, battery", [
    (topology, strategy, offloading, loadbalancing, battery)
    for topology, strategy, offloading, loadbalancing, battery in product(
        ["test", "prod"],                       # Topology
        ["reactive", "proactive", "oracle"],    # Strategies
        ["model", "data"],                      # Offloading
        [True, False],                          # Loadbalancing
        [True, False]                           # Battery
    )
])
def test_valid_strategies(base_config, topology, strategy, offloading, loadbalancing, battery):
    """Test valid strategies."""
    config = base_config.copy()
    config["topology"] = topology
    config["strategy"] = strategy
    config["offloading"] = offloading
    config["loadbalancing"] = loadbalancing
    config["battery"]["enabled"] = battery

    config_path = write_temp_config(config)
    try:
        assert sim.main(config_file=config_path) is True, f"strategy {strategy} with offloading '{offloading}' failed"
    finally:
        os.remove(config_path)

def test_invalid_strategy(base_config):
    """Test invalid strategy."""
    config = base_config.copy()
    config["strategy"] = "invalid_strategy"

    config_path = write_temp_config(config)
    try:
        assert sim.main(config_file=config_path) is False, "Invalid strategy should return False"
    finally:
        os.remove(config_path)

def test_invalid_offloading(base_config):
    """Test invalid offloading."""
    config = base_config.copy()
    config["offloading"] = "invalid_offloading"

    config_path = write_temp_config(config)
    try:
        assert sim.main(config_file=config_path) is False, "Invalid offloading should return False"
    finally:
        os.remove(config_path)
