from esphome import pins
import esphome.config_validation as cv
import esphome.codegen as cg
from esphome.const import (
    CONF_DOMAIN,
    CONF_ID,
    CONF_MANUAL_IP,
    CONF_STATIC_IP,
    CONF_USE_ADDRESS,
    CONF_GATEWAY,
    CONF_SUBNET,
    CONF_DNS1,
    CONF_DNS2,
)
from esphome.core import CORE, coroutine_with_priority
from esphome.components.network import ip_address_literal

CONFLICTS_WITH = []
DEPENDENCIES = ["rp2040"]
AUTO_LOAD = ["network"]

ethernet_ns = cg.esphome_ns.namespace("w5500_ethernet")

MANUAL_IP_SCHEMA = cv.Schema(
    {
        cv.Required(CONF_STATIC_IP): cv.ipv4address,
        cv.Required(CONF_GATEWAY): cv.ipv4address,
        cv.Required(CONF_SUBNET): cv.ipv4address,
        cv.Optional(CONF_DNS1, default="0.0.0.0"): cv.ipv4address,
        cv.Optional(CONF_DNS2, default="0.0.0.0"): cv.ipv4address,
    }
)

EthernetComponent = ethernet_ns.class_("W5500EthernetComponent", cg.Component)
ManualIP = ethernet_ns.struct("ManualIP")


def _validate(config):
    if CONF_USE_ADDRESS not in config:
        if CONF_MANUAL_IP in config:
            use_address = str(config[CONF_MANUAL_IP][CONF_STATIC_IP])
        else:
            use_address = CORE.name + config[CONF_DOMAIN]
        config[CONF_USE_ADDRESS] = use_address
    return config


CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(EthernetComponent),
            cv.Optional(CONF_MANUAL_IP): MANUAL_IP_SCHEMA,
            cv.Optional(CONF_DOMAIN, default=".local"): cv.domain_name,
            cv.Optional(CONF_USE_ADDRESS): cv.string_strict,
        }
    ).extend(cv.COMPONENT_SCHEMA),
    _validate,
)


def manual_ip(config):
    return cg.StructInitializer(
        ManualIP,
        ("static_ip", ip_address_literal(config[CONF_STATIC_IP])),
        ("gateway", ip_address_literal(config[CONF_GATEWAY])),
        ("subnet", ip_address_literal(config[CONF_SUBNET])),
        ("dns1", ip_address_literal(config[CONF_DNS1])),
        ("dns2", ip_address_literal(config[CONF_DNS2])),
    )


@coroutine_with_priority(60.0)
async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    cg.add(var.set_use_address(config[CONF_USE_ADDRESS]))

    if CONF_MANUAL_IP in config:
        cg.add(var.set_manual_ip(manual_ip(config[CONF_MANUAL_IP])))

    cg.add_define("USE_W5500_ETHERNET")
