// Paste into the JavaScript editor in MakeCode after adding "bluetooth".
bluetooth.onBluetoothConnected(function () {
    basic.showIcon(IconNames.Yes)
})

bluetooth.onBluetoothDisconnected(function () {
    basic.clearScreen()
})

bluetooth.onUartDataReceived(serial.delimiters(Delimiters.NewLine), function () {
    let command = bluetooth.uartReadUntil(serial.delimiters(Delimiters.NewLine))
    if (command == "ON") {
        basic.showLeds(`
            # # # # #
            # # # # #
            # # # # #
            # # # # #
            # # # # #
        `)
    } else if (command == "OFF") {
        basic.clearScreen()
    } else if (command == "HEART") {
        basic.showIcon(IconNames.Heart)
    } else {
        let fields = command.split(",")
        if (fields.length == 4 && fields[0] == "PIXEL") {
            let x = parseInt(fields[1])
            let y = parseInt(fields[2])
            if (x >= 0 && x <= 4 && y >= 0 && y <= 4) {
                if (fields[3] == "1") {
                    led.plot(x, y)
                } else if (fields[3] == "0") {
                    led.unplot(x, y)
                }
            }
        }
    }
})

bluetooth.startUartService()
basic.showIcon(IconNames.SmallDiamond)
