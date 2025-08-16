#!/usr/bin/swift

import Cocoa
import Foundation

// MARK: - Key Interceptor Core

class KeyInterceptor {
    // MARK: Properties
    private var eventTap: CFMachPort?
    private var runLoopSource: CFRunLoopSource?
    private var isActive = false
    private let outputFile: String
    private var fileHandle: FileHandle?
    
    // State tracking
    private var lastModifierFlags: CGEventFlags = []
    private let toggleKey: (keyCode: Int64, flags: CGEventFlags) = (27, [.maskCommand, .maskShift]) // Cmd+Shift+-
    
    // Performance
    private let writeQueue = DispatchQueue(label: "com.hotkeytrainer.writequeue", qos: .userInitiated)
    
    // MARK: Key Mappings
    private let keyMap: [Int: String] = [
        // Special keys
        48: "tab", 49: "space", 36: "return", 51: "delete", 117: "forwarddelete",
        53: "escape", 123: "left", 124: "right", 125: "down", 126: "up",
        115: "home", 119: "end", 116: "pageup", 121: "pagedown",
        
        // Function keys
        122: "f1", 120: "f2", 99: "f3", 118: "f4", 96: "f5", 97: "f6",
        98: "f7", 100: "f8", 101: "f9", 109: "f10", 103: "f11", 111: "f12",
        
        // Letters (QWERTY layout)
        0: "a", 11: "b", 8: "c", 2: "d", 14: "e", 3: "f", 5: "g", 4: "h",
        34: "i", 38: "j", 40: "k", 37: "l", 46: "m", 45: "n", 31: "o",
        35: "p", 12: "q", 15: "r", 1: "s", 17: "t", 32: "u", 9: "v",
        13: "w", 7: "x", 16: "y", 6: "z",
        
        // Numbers
        18: "1", 19: "2", 20: "3", 21: "4", 23: "5",
        22: "6", 26: "7", 28: "8", 25: "9", 29: "0",
        
        // Punctuation
        27: "-", 24: "=", 33: "[", 30: "]", 42: "\\",
        41: ";", 39: "'", 43: ",", 47: ".", 44: "/", 50: "`"
    ]
    
    // Map page navigation keys back to arrow keys when fn is detected
    // This handles keyboards that send pageup/pagedown/home/end instead of arrows with fn
    private let fnRemapping: [Int: String] = [
        116: "up",      // pageup -> up
        121: "down",    // pagedown -> down
        115: "left",    // home -> left
        119: "right"    // end -> right
    ]
    
    // Keys that should ignore the fn modifier when pressed alone
    // (Arrow keys often send fn flag on some Mac keyboards)
    private let ignoreFnForKeys: Set<Int> = [
        123, 124, 125, 126,  // Arrow keys
        115, 119, 116, 121   // home, end, pageup, pagedown
    ]
    
    // Modifier-only keycodes (for detecting solo modifier presses)
    private let modifierKeyCodes: Set<Int64> = [
        54, 55,  // Cmd (right, left)
        56, 60,  // Shift (left, right) 
        58, 61,  // Alt/Option (left, right)
        59, 62,  // Ctrl (left, right)
        63,      // Fn
        57       // Caps Lock
    ]
    
    // MARK: Initialization
    init() {
        let home = FileManager.default.homeDirectoryForCurrentUser.path
        self.outputFile = "\(home)/hotkey-trainer/captured_keys.txt"
        
        // Create directory if needed
        let dir = "\(home)/hotkey-trainer"
        try? FileManager.default.createDirectory(
            atPath: dir,
            withIntermediateDirectories: true,
            attributes: nil
        )
    }
    
    // MARK: Event Callback
    private static let eventCallback: CGEventTapCallBack = { proxy, type, event, refcon in
        let interceptor = Unmanaged<KeyInterceptor>.fromOpaque(refcon!).takeUnretainedValue()
        
        // Handle tap timeout
        if type == .tapDisabledByTimeout {
            CGEvent.tapEnable(tap: interceptor.eventTap!, enable: true)
            return Unmanaged.passRetained(event)
        }
        
        let keyCode = event.getIntegerValueField(.keyboardEventKeycode)
        let flags = event.flags
        
        // Check for toggle shortcut (allow it through)
        if interceptor.isToggleShortcut(keyCode: keyCode, flags: flags, type: type) {
            if type == .keyDown {
                interceptor.toggle()
            }
            return Unmanaged.passRetained(event)
        }
        
        // Pass through if not active
        guard interceptor.isActive else {
            return Unmanaged.passRetained(event)
        }
        
        // Handle different event types
        switch type {
        case .keyDown:
            interceptor.handleKeyDown(keyCode: keyCode, flags: flags, event: event)
            return nil // Block the event
            
        case .keyUp:
            // Block key up but don't log
            return nil
            
        case .flagsChanged:
            interceptor.handleFlagsChanged(keyCode: keyCode, flags: flags)
            return nil // Block modifier events
            
        default:
            return nil
        }
    }
    
    // MARK: Event Handling
    private func isToggleShortcut(keyCode: Int64, flags: CGEventFlags, type: CGEventType) -> Bool {
        // Only respond to keyDown for toggle
        guard type == .keyDown else { return false }
        
        // Check if it's our toggle combo
        let requiredFlags: CGEventFlags = [.maskCommand, .maskShift]
        let hasRequiredFlags = flags.contains(requiredFlags)
        let noExtraModifiers = !flags.contains(.maskControl) && !flags.contains(.maskAlternate)
        
        return keyCode == toggleKey.keyCode && hasRequiredFlags && noExtraModifiers
    }
    
    private func handleKeyDown(keyCode: Int64, flags: CGEventFlags, event: CGEvent) {
        // Skip pure modifier keys (they're handled in flagsChanged)
        guard !modifierKeyCodes.contains(keyCode) else { return }
        
        // Build the key combination string
        var parts: [String] = []
        
        // Get the base key name
        var keyName = getKeyName(for: Int(keyCode), event: event)
        
        // Check if we should skip the fn modifier
        var shouldSkipFn = false
        
        // Case 1: Arrow keys (123-126) with fn flag should ignore fn
        let arrowKeyCodes: Set<Int> = [123, 124, 125, 126]
        if arrowKeyCodes.contains(Int(keyCode)) && flags.contains(.maskSecondaryFn) {
            shouldSkipFn = true
        }
        
        // Case 2: Page navigation keys with fn that should be remapped to arrows
        if flags.contains(.maskSecondaryFn) {
            if let remapped = fnRemapping[Int(keyCode)] {
                keyName = remapped
                shouldSkipFn = true
            }
        }
        
        // Add modifiers in consistent order
        if flags.contains(.maskControl) { parts.append("ctrl") }
        if flags.contains(.maskAlternate) { parts.append("alt") }
        if flags.contains(.maskShift) { parts.append("shift") }
        if flags.contains(.maskCommand) { parts.append("cmd") }
        
        // Only add fn if we're not skipping it
        if flags.contains(.maskSecondaryFn) && !shouldSkipFn {
            parts.append("fn")
        }
        
        // Add the main key
        parts.append(keyName)
        
        // Write the combination
        let output = parts.joined(separator: "+")
        writeKey(output)
    }
    
    private func handleFlagsChanged(keyCode: Int64, flags: CGEventFlags) {
        // Detect solo modifier key presses
        let modifierPressed = !flags.isEmpty && modifierKeyCodes.contains(keyCode)
        let modifiersChanged = flags != lastModifierFlags
        
        if modifierPressed && modifiersChanged {
            // Determine which modifier was pressed
            var modifierName: String?
            
            // Check what changed
            if flags.contains(.maskCommand) && !lastModifierFlags.contains(.maskCommand) {
                modifierName = "cmd"
            } else if flags.contains(.maskShift) && !lastModifierFlags.contains(.maskShift) {
                modifierName = "shift"
            } else if flags.contains(.maskAlternate) && !lastModifierFlags.contains(.maskAlternate) {
                modifierName = "alt"
            } else if flags.contains(.maskControl) && !lastModifierFlags.contains(.maskControl) {
                modifierName = "ctrl"
            } else if flags.contains(.maskSecondaryFn) && !lastModifierFlags.contains(.maskSecondaryFn) {
                modifierName = "fn"
            } else if keyCode == 57 { // Caps Lock toggle
                modifierName = "capslock"
            }
            
            if let name = modifierName {
                writeKey(name)
            }
        }
        
        lastModifierFlags = flags
    }
    
    private func getKeyName(for keyCode: Int, event: CGEvent) -> String {
        // Check our mapping first
        if let mapped = keyMap[keyCode] {
            return mapped
        }
        
        // Try to get the actual character
        var length: Int = 0
        event.keyboardGetUnicodeString(maxStringLength: 1, actualStringLength: &length, unicodeString: nil)
        
        if length > 0 {
            var chars = [UniChar](repeating: 0, count: 1)
            event.keyboardGetUnicodeString(maxStringLength: 1, actualStringLength: nil, unicodeString: &chars)
            
            if let char = String(utf16CodeUnits: chars, count: 1).lowercased().first {
                return String(char)
            }
        }
        
        // Fallback to key code
        return "key\(keyCode)"
    }
    
    // MARK: File Operations
    private func writeKey(_ key: String) {
        writeQueue.async { [weak self] in
            guard let self = self,
                  let fileHandle = self.fileHandle,
                  let data = "\(key)\n".data(using: .utf8) else { return }
            
            fileHandle.write(data)
            fileHandle.synchronizeFile()
        }
    }
    
    // MARK: Activation Control
    private func toggle() {
        if isActive {
            deactivate()
        } else {
            activate()
        }
    }
    
    private func activate() {
        isActive = true
        lastModifierFlags = []
        
        // Create/open file for writing
        FileManager.default.createFile(atPath: outputFile, contents: nil)
        fileHandle = FileHandle(forWritingAtPath: outputFile)
        
        showNotification(title: "🔴 Trainer ON", message: "Keys are being captured")
        print("🔴 Trainer ON - Keys blocked")
    }
    
    private func deactivate() {
        isActive = false
        
        // Close and remove file
        writeQueue.sync {
            fileHandle?.closeFile()
            fileHandle = nil
        }
        try? FileManager.default.removeItem(atPath: outputFile)
        
        showNotification(title: "🟢 Trainer OFF", message: "Keys are normal")
        print("🟢 Trainer OFF - Keys normal")
    }
    
    // MARK: Notifications
    private func showNotification(title: String, message: String) {
        // Simple console output instead of deprecated NSUserNotification
        // For a production app, you'd use UserNotifications framework
        // but that requires more setup and an app bundle
        DispatchQueue.main.async {
            // Could implement UserNotifications here if needed
            // For now, just rely on console output
        }
    }
    
    // MARK: Public Interface
    func start() {
        // Check for accessibility permissions
        checkAccessibilityPermissions()
        
        // Create event tap for multiple event types
        let eventMask = CGEventMask(
            (1 << CGEventType.keyDown.rawValue) |
            (1 << CGEventType.keyUp.rawValue) |
            (1 << CGEventType.flagsChanged.rawValue)
        )
        
        eventTap = CGEvent.tapCreate(
            tap: .cgSessionEventTap,
            place: .headInsertEventTap,
            options: .defaultTap,
            eventsOfInterest: eventMask,
            callback: KeyInterceptor.eventCallback,
            userInfo: Unmanaged.passUnretained(self).toOpaque()
        )
        
        guard let eventTap = eventTap else {
            print("❌ Failed to create event tap")
            print("Make sure Terminal has Accessibility permissions")
            exit(1)
        }
        
        // Create run loop source
        runLoopSource = CFMachPortCreateRunLoopSource(kCFAllocatorDefault, eventTap, 0)
        CFRunLoopAddSource(CFRunLoopGetCurrent(), runLoopSource, .commonModes)
        
        // Enable the tap
        CGEvent.tapEnable(tap: eventTap, enable: true)
        
        // Show ready message
        print("🎮 HotKey Trainer Ready!")
        print("Toggle with: Cmd+Shift+-")
        print("Quit with: Ctrl+C")
        print("")
        print("Status indicators:")
        print("  🔴 = Trainer ON (keys blocked)")
        print("  🟢 = Trainer OFF (keys normal)")
        print("")
        
        // Run the event loop
        CFRunLoopRun()
    }
    
    func stop() {
        // Disable tap
        if let eventTap = eventTap {
            CGEvent.tapEnable(tap: eventTap, enable: false)
        }
        
        // Remove from run loop
        if let runLoopSource = runLoopSource {
            CFRunLoopRemoveSource(CFRunLoopGetCurrent(), runLoopSource, .commonModes)
        }
        
        // Deactivate if active
        if isActive {
            deactivate()
        }
        
        // Stop run loop
        CFRunLoopStop(CFRunLoopGetCurrent())
    }
    
    private func checkAccessibilityPermissions() {
        let options = [kAXTrustedCheckOptionPrompt.takeUnretainedValue(): true] as CFDictionary
        let trusted = AXIsProcessTrustedWithOptions(options)
        
        if !trusted {
            print("⚠️  Accessibility Permission Required")
            print("")
            print("Please grant accessibility permission to Terminal:")
            print("1. Open System Preferences")
            print("2. Go to Security & Privacy → Privacy → Accessibility")
            print("3. Click the lock to make changes")
            print("4. Add and check ✅ Terminal (or iTerm/your terminal app)")
            print("")
            print("After granting permission, please restart this app.")
            exit(1)
        }
    }
}

// MARK: - Signal Handler

class SignalHandler {
    private static var interceptor: KeyInterceptor?
    
    static func setup(with interceptor: KeyInterceptor) {
        self.interceptor = interceptor
        
        // Handle Ctrl+C gracefully
        signal(SIGINT) { _ in
            print("\n\n👋 Shutting down...")
            SignalHandler.interceptor?.stop()
            exit(0)
        }
        
        // Handle termination
        signal(SIGTERM) { _ in
            SignalHandler.interceptor?.stop()
            exit(0)
        }
    }
}

// MARK: - Main Entry Point

let interceptor = KeyInterceptor()
SignalHandler.setup(with: interceptor)
interceptor.start()