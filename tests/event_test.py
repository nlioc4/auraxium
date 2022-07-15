"""Tests for the real-time event client module."""

import asyncio
import unittest

# pylint: disable=import-error
import auraxium

from tests.utils import SERVICE_ID


@unittest.skipIf(SERVICE_ID == 's:example', 'missing service ID')
class EventClientTest(unittest.IsolatedAsyncioTestCase):
    """Live tests for the real-time event client component."""

    client: auraxium.EventClient

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.client = auraxium.EventClient(service_id=SERVICE_ID)

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()
        await self.client.close()

    def test_startup_defensive(self) -> None:
        """Ensure the client does not connect without any triggers."""
        self.assertFalse(self.client.triggers, 'predefined triggers')
        self.assertIsNone(self.client.websocket, 'websocket without triggers')

    async def test_connect_on_trigger(self) -> None:
        """Ensure the client connects as soon as a trigger is added."""
        self.assertFalse(self.client.triggers, 'predefined triggers found')
        self.assertIsNone(self.client.websocket, 'preexisting websocket found')
        # Add trigger and wait for ready
        trigger = auraxium.Trigger(auraxium.event.BattleRankUp)
        self.client.add_trigger(trigger)
        await self.client.wait_ready()
        # Check for websocket activity
        self.assertIsNotNone(self.client.websocket, 'missing websocket')
        self.assertListEqual(
            self.client.triggers, [trigger], 'trigger not found')

    async def test_messages(self) -> None:
        """Test event dispatching."""
        flag = asyncio.Event()

        async def on_death(event: auraxium.event.Event) -> None:
            self.assertIsInstance(event, auraxium.event.Event,
                                  'non-event returned')
            flag.set()

        # pylint: disable=not-callable
        self.client.trigger(auraxium.event.Death)(on_death)
        try:
            await asyncio.wait_for(flag.wait(), 5.0)
        except asyncio.TimeoutError:
            self.skipTest('no game event received after 5 seconds, '
                          'is the game in maintenance?')
        self.assertEqual(len(self.client.triggers), 1)
        self.client.remove_trigger('on_death')
        self.assertEqual(len(self.client.triggers), 0)

    async def test_single_shot(self) -> None:
        """Test a single-shot trigger to ensure it is auto-deleted."""
        trigger = auraxium.Trigger(auraxium.event.Death, single_shot=True)
        flag = asyncio.Event()

        async def wait_for(event: auraxium.event.Event) -> None:
            _ = event
            flag.set()

        trigger.action = wait_for
        self.client.add_trigger(trigger)
        try:
            await asyncio.wait_for(flag.wait(), 5.0)
        except asyncio.TimeoutError:
            self.skipTest('no game event received after 5 seconds, '
                          'is the game in maintenance?')
        self.assertEqual(len(self.client.triggers), 0)
