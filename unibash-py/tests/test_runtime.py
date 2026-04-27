import unittest

from runtime.context import RuntimeContext
from runtime.exceptions import (
    DuplicateNameError,
    InvalidTargetError,
    MissingReferenceError,
)
from runtime.models import Group, Host, Range
from runtime.resolver import TargetResolver


class TestRuntimeContext(unittest.TestCase):
    def setUp(self):
        self.context = RuntimeContext()

    def test_register_host(self):
        h = Host(name="web1", address="192.168.1.10")
        self.context.register_host(h)
        self.assertEqual(self.context.get_host("web1"), h)

    def test_duplicate_entity(self):
        h = Host(name="web1", address="192.168.1.10")
        self.context.register_host(h)
        with self.assertRaises(DuplicateNameError):
            self.context.register_host(h)

        with self.assertRaises(DuplicateNameError):
            self.context.register_group(Group(name="web1", members=[]))

    def test_set_get_variable(self):
        self.context.set_variable("port", 8080)
        self.assertEqual(self.context.get_variable("port"), 8080)

        # Variable collision with static entity
        self.context.register_host(Host(name="db1", address="10.0.0.1"))
        with self.assertRaises(DuplicateNameError):
            self.context.set_variable("db1", "conflict")

    def test_missing_reference(self):
        with self.assertRaises(MissingReferenceError):
            self.context.get_host("nonexistent")


class TestTargetResolver(unittest.TestCase):
    def setUp(self):
        self.context = RuntimeContext()
        self.resolver = TargetResolver(self.context)

    def test_resolve_literal_ip(self):
        hosts = self.resolver.resolve("192.168.1.50")
        self.assertEqual(len(hosts), 1)
        self.assertEqual(hosts[0].name, "192.168.1.50")
        self.assertEqual(hosts[0].address, "192.168.1.50")

    def test_resolve_host(self):
        h = Host(name="web1", address="10.0.0.1")
        self.context.register_host(h)
        hosts = self.resolver.resolve("web1")
        self.assertEqual(len(hosts), 1)
        self.assertEqual(hosts[0], h)

    def test_resolve_group(self):
        self.context.register_host(Host(name="web1", address="10.0.0.1"))
        self.context.register_host(Host(name="web2", address="10.0.0.2"))
        self.context.register_group(Group(name="web_servers", members=["web1", "web2"]))

        hosts = self.resolver.resolve("web_servers")
        self.assertEqual(len(hosts), 2)
        names = [h.name for h in hosts]
        self.assertIn("web1", names)
        self.assertIn("web2", names)

    def test_resolve_nested_group(self):
        self.context.register_host(Host(name="db1", address="10.0.1.1"))
        self.context.register_host(Host(name="web1", address="10.0.0.1"))

        self.context.register_group(Group(name="dbs", members=["db1"]))
        self.context.register_group(Group(name="webs", members=["web1"]))
        self.context.register_group(Group(name="all_servers", members=["dbs", "webs"]))

        hosts = self.resolver.resolve("all_servers")
        self.assertEqual(len(hosts), 2)
        names = [h.name for h in hosts]
        self.assertIn("db1", names)
        self.assertIn("web1", names)

    def test_deduplication(self):
        self.context.register_host(Host(name="web1", address="10.0.0.1"))
        self.context.register_group(Group(name="g1", members=["web1"]))
        self.context.register_group(Group(name="g2", members=["web1"]))
        self.context.register_group(Group(name="all", members=["g1", "g2", "web1"]))

        hosts = self.resolver.resolve("all")
        self.assertEqual(len(hosts), 1)
        self.assertEqual(hosts[0].name, "web1")

    def test_invalid_target(self):
        with self.assertRaises(InvalidTargetError):
            self.resolver.resolve("nonexistent_entity")


if __name__ == "__main__":
    unittest.main()
