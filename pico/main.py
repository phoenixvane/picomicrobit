"""Pico 2 W / MicroPython: control a micro:bit V2 over BLE UART."""

import asyncio
import bluetooth
import aioble
from machine import Pin
from time import ticks_ms, ticks_diff


UART_SERVICE = bluetooth.UUID("6e400001-b5a3-f393-e0a9-e50e24dcca9e")
UART_RX = bluetooth.UUID("6e400003-b5a3-f393-e0a9-e50e24dcca9e")

# Copy the exact advertised name printed during scanning if several boards exist.
TARGET_NAME = None

# External normally-open button: GP15 (physical pin 20) to GND (pin 18).
BUTTON_PIN = 15
DEBOUNCE_MS = 50


async def find_microbit():
    async with aioble.scan(10000, interval_us=30000, window_us=30000,
                           active=True) as scanner:
        async for result in scanner:
            name = result.name() or ""
            if name:
                print("Found:", name, result.device)
            matches = (name == TARGET_NAME if TARGET_NAME else
                       name.lower().startswith("micro:bit"))
            if matches:
                return result.device
    return None


class MicrobitLED:
    def __init__(self, rx):
        self.rx = rx

    async def command(self, text):
        # Newline is the message delimiter used by the MakeCode program.
        await self.rx.write((text + "\n").encode(), response=True)

    async def on(self):
        await self.command("ON")

    async def off(self):
        await self.command("OFF")

    async def heart(self):
        await self.command("HEART")

    async def pixel(self, x, y, enabled=True):
        if not (0 <= x <= 4 and 0 <= y <= 4):
            raise ValueError("x and y must be between 0 and 4")
        await self.command("PIXEL,{},{},{}".format(x, y, int(bool(enabled))))


async def main():
    button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
    while True:
        try:
            print("Scanning for micro:bit...")
            device = await find_microbit()
            if device is None:
                print("Not found. Check power and MakeCode Bluetooth settings.")
                await asyncio.sleep(2)
                continue

            async with await device.connect(timeout_ms=10000) as connection:
                service = await connection.service(UART_SERVICE)
                if service is None:
                    raise RuntimeError("Bluetooth UART service is missing")
                rx = await service.characteristic(UART_RX)
                if rx is None:
                    raise RuntimeError("Bluetooth UART RX characteristic is missing")
                display = MicrobitLED(rx)
                await display.off()
                state = 0
                last_reading = button.value()
                stable_reading = last_reading
                changed_at = ticks_ms()
                print("Connected. Press the GP15 button to change the display.")
                while connection.is_connected():
                    reading = button.value()
                    if reading != last_reading:
                        last_reading = reading
                        changed_at = ticks_ms()
                    if (reading != stable_reading and
                            ticks_diff(ticks_ms(), changed_at) >= DEBOUNCE_MS):
                        stable_reading = reading
                        if stable_reading == 0:
                            # Advance only on a debounced press, not while held.
                            state = (state + 1) % 4
                            if state == 1:
                                await display.on()
                            elif state == 2:
                                await display.heart()
                            elif state == 3:
                                await display.off()
                                await display.pixel(2, 2)
                            else:
                                await display.off()
                    await asyncio.sleep_ms(10)
        except (OSError, asyncio.TimeoutError, RuntimeError) as error:
            print("BLE error:", error)
        await asyncio.sleep(2)


asyncio.run(main())
