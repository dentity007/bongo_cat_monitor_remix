#!/usr/bin/env python3
"""
Bongo Cat Settings GUI
Tkinter-based configuration interface for all application settings
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Optional, Callable

import settings
from sensors import read_sensors, is_admin_windows

class BongoCatSettingsGUI:
    """Settings GUI for Bongo Cat application"""
    
    def __init__(self, config_manager=None, engine=None, on_close_callback: Optional[Callable] = None, parent_root=None):
        """Initialize the settings GUI"""
        self.config = config_manager
        self.engine = engine
        self.on_close_callback = on_close_callback
        self.parent_root = parent_root  # Optional parent tkinter root
        self.window = None
        self.widgets = {}
        
        # Track if changes were made
        self.changes_made = False
        self.original_config = None
        
        # Configuration change tracking
        self.updating_from_config = False
        
        # Don't auto-create window during init to allow proper parent setup
        # Window will be created when show() is called
    
    def create_window(self):
        """Create and setup the settings window"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_set()
            return
        
        # Use parent root if provided, otherwise ensure we have a root window
        if self.parent_root:
            # Use the provided parent root
            root = self.parent_root
        elif not tk._default_root:
            # Create a hidden root window if none exists
            root = tk.Tk()
            root.withdraw()  # Hide it
        else:
            root = tk._default_root
        
        # Create main window as Toplevel with proper parent
        self.window = tk.Toplevel(root)
        self.window.title("Bongo Cat Settings")
        self.window.geometry("500x600")
        self.window.resizable(True, True)
        
        # Set window icon (if available)
        try:
            self.window.iconbitmap("assets/tray_icon.ico")
        except:
            pass  # Icon file not found, continue without it
        
        # Set up proper close handling
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        # Make window stay on top initially, then allow normal behavior
        self.window.attributes('-topmost', True)
        self.window.after(100, lambda: self.window.attributes('-topmost', False))
        
        # Store original configuration for comparison
        if self.config:
            self.original_config = {
                'display': self.config.get_display_settings().copy(),
                'behavior': self.config.get_behavior_settings().copy(),
                'connection': self.config.get_connection_settings().copy(),
                'startup': self.config.get_startup_settings().copy()
            }
        
        # Create all GUI content
        self.create_gui_content()
        
        # Load current settings into the GUI
        self.load_current_settings()
    
    def create_gui_content(self):
        """Create all GUI content (tabs, buttons, etc.)"""
        try:
            # Create notebook for tabs
            notebook = ttk.Notebook(self.window)
            notebook.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Create tabs
            self.create_display_tab(notebook)
            self.create_behavior_tab(notebook)
            self.create_connection_tab(notebook)
            self.create_startup_tab(notebook)
            self.create_advanced_tab(notebook)
            
            # Create button frame
            button_frame = ttk.Frame(self.window)
            button_frame.pack(fill='x', padx=10, pady=(0, 10))
            
            # Add buttons
            ttk.Button(button_frame, text="Apply", command=self.apply_settings).pack(side='right', padx=(5, 0))
            ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side='right', padx=(5, 0))
            ttk.Button(button_frame, text="Cancel", command=self.cancel_settings).pack(side='right', padx=(5, 0))
            ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_to_defaults).pack(side='left')
            
            # Setup change tracking after all widgets are created
            self.setup_change_tracking()
            
            print("✅ GUI content created successfully")
            
        except Exception as e:
            print(f"❌ Error creating GUI content: {e}")
            import traceback
            traceback.print_exc()
            # If content creation fails, at least make window closeable
            if self.window:
                self.window.destroy()
                self.window = None
    
    def create_display_tab(self, notebook):
        """Create the display settings tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Display")
        
        # Main container with padding
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Display elements section
        display_group = ttk.LabelFrame(main_frame, text="Display Elements", padding=15)
        display_group.pack(fill='x', pady=(0, 15))
        
        # Checkboxes for display elements
        self.widgets['show_cpu'] = tk.BooleanVar()
        ttk.Checkbutton(display_group, text="Show CPU Usage", 
                       variable=self.widgets['show_cpu'], command=self.on_setting_changed).pack(anchor='w', pady=2)
        
        self.widgets['show_ram'] = tk.BooleanVar()
        ttk.Checkbutton(display_group, text="Show RAM Usage", 
                       variable=self.widgets['show_ram'], command=self.on_setting_changed).pack(anchor='w', pady=2)
        
        self.widgets['show_wpm'] = tk.BooleanVar()
        ttk.Checkbutton(display_group, text="Show WPM Counter", 
                       variable=self.widgets['show_wpm'], command=self.on_setting_changed).pack(anchor='w', pady=2)
        
        self.widgets['show_time'] = tk.BooleanVar()
        ttk.Checkbutton(display_group, text="Show Clock", 
                       variable=self.widgets['show_time'], command=self.on_setting_changed).pack(anchor='w', pady=2)
        
        # Hardware monitoring options (chriss158 contribution)
        ttk.Separator(display_group, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(display_group, text="Hardware Monitoring (Advanced):", font=('TkDefaultFont', 9, 'bold')).pack(anchor='w', pady=(5, 2))
        
        self.widgets['show_cpu_temp'] = tk.BooleanVar()
        cpu_temp_cb = ttk.Checkbutton(display_group, text="Show CPU Temperature", 
                                     variable=self.widgets['show_cpu_temp'], command=self.on_setting_changed)
        cpu_temp_cb.pack(anchor='w', pady=2)
        
        self.widgets['show_gpu_temp'] = tk.BooleanVar()
        gpu_temp_cb = ttk.Checkbutton(display_group, text="Show GPU Temperature", 
                                     variable=self.widgets['show_gpu_temp'], command=self.on_setting_changed)
        gpu_temp_cb.pack(anchor='w', pady=2)
        
        # Hardware monitoring status
        self.widgets['hardware_status'] = ttk.Label(display_group, text="", font=('TkDefaultFont', 8), foreground='blue')
        self.widgets['hardware_status'].pack(anchor='w', pady=(5, 0))
        
        # Time format section
        time_group = ttk.LabelFrame(main_frame, text="Time Format", padding=15)
        time_group.pack(fill='x', pady=(0, 15))
        
        self.widgets['time_format'] = tk.StringVar(value="24")
        ttk.Radiobutton(time_group, text="24-hour format (14:30)", 
                       variable=self.widgets['time_format'], value="24", command=self.on_setting_changed).pack(anchor='w', pady=2)
        ttk.Radiobutton(time_group, text="12-hour format (2:30 PM)", 
                       variable=self.widgets['time_format'], value="12", command=self.on_setting_changed).pack(anchor='w', pady=2)
        
        # Preview section
        preview_group = ttk.LabelFrame(main_frame, text="Preview", padding=15)
        preview_group.pack(fill='x')
        
        self.widgets['preview_label'] = ttk.Label(preview_group, text="Changes will be applied to your Bongo Cat display", 
                                                 font=('TkDefaultFont', 9), foreground='gray')
        self.widgets['preview_label'].pack(anchor='w')
    
    def create_behavior_tab(self, notebook):
        """Create the behavior settings tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Behavior")
        
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Sleep settings
        sleep_group = ttk.LabelFrame(main_frame, text="Sleep Settings", padding=15)
        sleep_group.pack(fill='x', pady=(0, 15))
        
        ttk.Label(sleep_group, text="Sleep timeout (when cat goes to sleep):").pack(anchor='w', pady=(0, 5))
        
        timeout_frame = ttk.Frame(sleep_group)
        timeout_frame.pack(fill='x', pady=(0, 10))
        
        self.widgets['sleep_timeout'] = tk.IntVar(value=1)
        self.widgets['sleep_scale'] = ttk.Scale(timeout_frame, from_=1, to=60, orient='horizontal',
                                               variable=self.widgets['sleep_timeout'], command=self.on_sleep_timeout_changed)
        self.widgets['sleep_scale'].pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        self.widgets['sleep_label'] = ttk.Label(timeout_frame, text="1 minute", width=12)
        self.widgets['sleep_label'].pack(side='right')
        
        # Animation settings  
        anim_group = ttk.LabelFrame(main_frame, text="Animation Settings", padding=15)
        anim_group.pack(fill='x', pady=(0, 15))
        
        ttk.Label(anim_group, text="Idle timeout before stopping animations:").pack(anchor='w', pady=(0, 5))
        
        idle_frame = ttk.Frame(anim_group)
        idle_frame.pack(fill='x')
        
        self.widgets['idle_timeout'] = tk.DoubleVar(value=3.0)
        self.widgets['idle_scale'] = ttk.Scale(idle_frame, from_=0.5, to=10.0, orient='horizontal',
                                              variable=self.widgets['idle_timeout'], command=self.on_idle_timeout_changed)
        self.widgets['idle_scale'].pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        self.widgets['idle_label'] = ttk.Label(idle_frame, text="3.0 seconds", width=12)
        self.widgets['idle_label'].pack(side='right')
    
    def create_connection_tab(self, notebook):
        """Create the connection settings tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Connection")
        
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # COM port settings
        port_group = ttk.LabelFrame(main_frame, text="COM Port Settings", padding=15)
        port_group.pack(fill='x', pady=(0, 15))
        
        ttk.Label(port_group, text="COM Port:").pack(anchor='w', pady=(0, 5))
        
        port_frame = ttk.Frame(port_group)
        port_frame.pack(fill='x', pady=(0, 10))
        
        self.widgets['com_port'] = tk.StringVar(value="AUTO")
        port_combo = ttk.Combobox(port_frame, textvariable=self.widgets['com_port'], width=15)
        port_combo['values'] = ('AUTO', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8')
        port_combo.pack(side='left', padx=(0, 10))
        port_combo.bind('<<ComboboxSelected>>', lambda e: self.on_setting_changed())
        
        ttk.Button(port_frame, text="Scan Ports", command=self.scan_ports).pack(side='left')
        
        ttk.Label(port_group, text="Baudrate:").pack(anchor='w', pady=(10, 5))
        
        self.widgets['baudrate'] = tk.IntVar(value=115200)
        baud_combo = ttk.Combobox(port_group, textvariable=self.widgets['baudrate'], width=15)
        baud_combo['values'] = (9600, 19200, 38400, 57600, 115200)
        baud_combo.pack(anchor='w')
        baud_combo.bind('<<ComboboxSelected>>', lambda e: self.on_setting_changed())
        
        # Connection options
        conn_group = ttk.LabelFrame(main_frame, text="Connection Options", padding=15)
        conn_group.pack(fill='x', pady=(0, 15))
        
        self.widgets['auto_reconnect'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(conn_group, text="Auto-reconnect if connection lost", 
                       variable=self.widgets['auto_reconnect'], command=self.on_setting_changed).pack(anchor='w', pady=2)
        
        ttk.Label(conn_group, text="Connection timeout:").pack(anchor='w', pady=(10, 5))
        
        timeout_frame = ttk.Frame(conn_group)
        timeout_frame.pack(fill='x')
        
        self.widgets['conn_timeout'] = tk.IntVar(value=5)
        timeout_combo = ttk.Combobox(timeout_frame, textvariable=self.widgets['conn_timeout'], width=10)
        timeout_combo['values'] = (1, 2, 3, 5, 10, 15, 30)
        timeout_combo.pack(side='left', padx=(0, 5))
        timeout_combo.bind('<<ComboboxSelected>>', lambda e: self.on_setting_changed())
        
        ttk.Label(timeout_frame, text="seconds").pack(side='left')
    
    def create_startup_tab(self, notebook):
        """Create the startup settings tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Startup")
        
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Startup behavior
        startup_group = ttk.LabelFrame(main_frame, text="Startup Behavior", padding=15)
        startup_group.pack(fill='x', pady=(0, 15))
        
        self.widgets['start_with_windows'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(startup_group, text="Start with Windows", 
                       variable=self.widgets['start_with_windows'], command=self.on_setting_changed).pack(anchor='w', pady=2)
        
        self.widgets['start_minimized'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(startup_group, text="Start minimized to system tray", 
                       variable=self.widgets['start_minimized'], command=self.on_setting_changed).pack(anchor='w', pady=2)
        
        self.widgets['show_notifications'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(startup_group, text="Show notifications", 
                       variable=self.widgets['show_notifications'], command=self.on_setting_changed).pack(anchor='w', pady=2)
        
        # Status info
        status_group = ttk.LabelFrame(main_frame, text="Status", padding=15)
        status_group.pack(fill='x')
        
        self.widgets['status_label'] = ttk.Label(status_group, text="", font=('TkDefaultFont', 9))
        self.widgets['status_label'].pack(anchor='w')
        
        self.update_status_info()
    
    def create_advanced_tab(self, notebook):
        """Create the advanced settings tab (chriss158 contribution)"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Advanced")

        main_frame = ttk.Frame(frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Hardware monitoring section
        hardware_group = ttk.LabelFrame(main_frame, text="Hardware Monitoring", padding=15)
        hardware_group.pack(fill='x', pady=(0, 15))

        # Consent gate - must be checked first
        consent_frame = ttk.Frame(hardware_group)
        consent_frame.pack(fill='x', pady=(0, 10))

        self.widgets['hardware_consent'] = tk.BooleanVar(value=False)
        consent_cb = ttk.Checkbutton(consent_frame,
                                   text="I consent to hardware temperature monitoring",
                                   variable=self.widgets['hardware_consent'],
                                   command=self.on_consent_changed)
        consent_cb.pack(anchor='w')

        consent_note = ttk.Label(consent_frame,
                               text="⚠️ This enables temperature monitoring of your hardware.\nData stays local and is not transmitted.",
                               font=('TkDefaultFont', 8),
                               foreground='orange',
                               wraplength=400,
                               justify='left')
        consent_note.pack(anchor='w', pady=(2, 0))

        # Enable/disable hardware monitoring (only enabled after consent)
        self.widgets['hardware_monitoring'] = tk.BooleanVar(value=False)
        enable_cb = ttk.Checkbutton(hardware_group, text="Enable hardware temperature monitoring",
                                   variable=self.widgets['hardware_monitoring'],
                                   command=self.on_setting_changed,
                                   state='disabled')  # Initially disabled
        enable_cb.pack(anchor='w', pady=(10, 5))

        # Provider selection
        provider_frame = ttk.Frame(hardware_group)
        provider_frame.pack(fill='x', pady=(5, 5))

        ttk.Label(provider_frame, text="Provider:").pack(side='left')
        self.widgets['hardware_provider'] = tk.StringVar(value='auto')
        provider_combo = ttk.Combobox(provider_frame, textvariable=self.widgets['hardware_provider'],
                                    values=['auto', 'lhm_http', 'nvml'], state='readonly', width=10)
        provider_combo.pack(side='left', padx=(5, 0))
        provider_combo.bind('<<ComboboxSelected>>', lambda e: self.on_setting_changed())

        # GPU-only mode (least privilege)
        self.widgets['gpu_only'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(hardware_group, text="GPU-only mode (recommended for least privilege)",
                       variable=self.widgets['gpu_only'], command=self.on_setting_changed).pack(anchor='w', pady=(5, 10))

        # Test button
        test_frame = ttk.Frame(hardware_group)
        test_frame.pack(fill='x', pady=(5, 10))

        ttk.Button(test_frame, text="Test Sensors", command=self.test_hardware_sensors).pack(side='left')
        self.widgets['test_status'] = ttk.Label(test_frame, text="", font=('TkDefaultFont', 8), foreground='green')
        self.widgets['test_status'].pack(side='left', padx=(10, 0))

        # Hardware status display
        status_frame = ttk.LabelFrame(hardware_group, text="Hardware Status", padding=10)
        status_frame.pack(fill='x', pady=(10, 0))

        self.widgets['hardware_info'] = ttk.Label(status_frame, text="Hardware monitoring: Disabled",
                                                font=('TkDefaultFont', 9))
        self.widgets['hardware_info'].pack(anchor='w')

        self.widgets['temp_display'] = ttk.Label(status_frame, text="", font=('TkDefaultFont', 8), foreground='blue')
        self.widgets['temp_display'].pack(anchor='w', pady=(5, 0))

        # Update hardware status
        self.update_hardware_status()
    
    def scan_ports(self):
        """Scan for available COM ports"""
        try:
            import serial.tools.list_ports
            ports = [port.device for port in serial.tools.list_ports.comports()]
            ports.insert(0, 'AUTO')
            
            # Update combobox values
            port_combo = None
            for widget in self.window.winfo_children():
                if isinstance(widget, ttk.Notebook):
                    for tab in widget.tabs():
                        tab_frame = widget.nametowidget(tab)
                        for child in tab_frame.winfo_children():
                            if isinstance(child, ttk.Frame):
                                for grandchild in child.winfo_children():
                                    if isinstance(grandchild, ttk.LabelFrame) and "COM Port" in grandchild['text']:
                                        for item in grandchild.winfo_children():
                                            if isinstance(item, ttk.Frame):
                                                for subitem in item.winfo_children():
                                                    if isinstance(subitem, ttk.Combobox):
                                                        port_combo = subitem
                                                        break
            
            if port_combo:
                port_combo['values'] = tuple(ports)
                messagebox.showinfo("Port Scan", f"Found {len(ports)-1} COM ports")
            else:
                messagebox.showinfo("Port Scan", f"Found ports: {', '.join(ports[1:]) if len(ports) > 1 else 'None'}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scan ports: {e}")
    
    def load_current_settings(self):
        """Load current settings from config manager into GUI"""
        if not self.config:
            return
        
        self.updating_from_config = True
        
        try:
            # Load display settings
            display = self.config.get_display_settings()
            self.widgets['show_cpu'].set(display.get('show_cpu', True))
            self.widgets['show_ram'].set(display.get('show_ram', True))
            self.widgets['show_wpm'].set(display.get('show_wpm', True))
            self.widgets['show_time'].set(display.get('show_time', True))
            self.widgets['time_format'].set('24' if display.get('time_format_24h', True) else '12')
            self.widgets['show_cpu_temp'].set(display.get('show_cpu_temp', False))
            self.widgets['show_gpu_temp'].set(display.get('show_gpu_temp', False))
            
            # Load advanced settings
            advanced = self.config.get_advanced_settings()
            self.widgets['hardware_monitoring'].set(advanced.get('hardware_monitoring', False))
            self.widgets['require_admin_for_cpu'].set(advanced.get('require_admin_for_cpu_temp', True))

            # Load telemetry settings (new consent-based system)
            try:
                from . import settings as app_settings
                telemetry_cfg = app_settings.load()
                telemetry = telemetry_cfg.get('telemetry', {})

                self.widgets['hardware_consent'].set(telemetry.get('hardware_monitoring_consented', False))
                self.widgets['hardware_provider'].set(telemetry.get('provider', 'auto'))
                self.widgets['gpu_only'].set(telemetry.get('gpu_only', True))

                # Update consent-dependent widgets
                self.on_consent_changed()

            except ImportError:
                # Fallback if settings module not available
                self.widgets['hardware_consent'].set(False)
                self.widgets['hardware_provider'].set('auto')
                self.widgets['gpu_only'].set(True)
            
            # Load behavior settings
            behavior = self.config.get_behavior_settings()
            self.widgets['sleep_timeout'].set(behavior.get('sleep_timeout_minutes', 1))
    
            self.widgets['idle_timeout'].set(behavior.get('idle_timeout_seconds', 3.0))
            
            # Load connection settings
            connection = self.config.get_connection_settings()
            self.widgets['com_port'].set(connection.get('com_port', 'AUTO'))
            self.widgets['baudrate'].set(connection.get('baudrate', 115200))
            self.widgets['auto_reconnect'].set(connection.get('auto_reconnect', True))
            self.widgets['conn_timeout'].set(connection.get('timeout_seconds', 5))
            
            # Load startup settings
            startup = self.config.get_startup_settings()
            self.widgets['start_with_windows'].set(startup.get('start_with_windows', True))
            self.widgets['start_minimized'].set(startup.get('start_minimized', True))
            self.widgets['show_notifications'].set(startup.get('show_notifications', True))
            
            # Update labels
            self.update_slider_labels()
            
        finally:
            self.updating_from_config = False
    
    def setup_change_tracking(self):
        """Setup change tracking for all widgets"""
        # This is already handled by the command callbacks in widget creation
        pass
    
    def on_setting_changed(self):
        """Called when any setting is changed"""
        if self.updating_from_config:
            return

        self.changes_made = True
        self.update_preview()

    def on_consent_changed(self):
        """Handle consent checkbox changes"""
        consented = self.widgets['hardware_consent'].get()

        # Enable/disable the monitoring checkbox based on consent
        if consented:
            self.widgets['hardware_monitoring'].config(state='normal')
        else:
            self.widgets['hardware_monitoring'].set(False)
            self.widgets['hardware_monitoring'].config(state='disabled')

        self.on_setting_changed()

    def test_hardware_sensors(self):
        """Test hardware sensor connectivity"""
        self.widgets['test_status'].config(text="Testing...", foreground='orange')
        self.window.update()

        try:
            # Import settings and sensors
            from . import settings, sensors

            # Load current config
            cfg = settings.load()

            # Update config with current GUI values
            cfg['telemetry']['hardware_monitoring_consented'] = self.widgets['hardware_consent'].get()
            cfg['telemetry']['hardware_monitoring_enabled'] = self.widgets['hardware_monitoring'].get()
            cfg['telemetry']['provider'] = self.widgets['hardware_provider'].get()
            cfg['telemetry']['gpu_only'] = self.widgets['gpu_only'].get()

            # Test the sensors
            monitor = sensors.HardwareMonitor(cfg)
            if monitor.test_connection():
                self.widgets['test_status'].config(text="✓ Connected", foreground='green')
            else:
                self.widgets['test_status'].config(text="✗ Failed", foreground='red')

        except ImportError as e:
            self.widgets['test_status'].config(text=f"✗ Missing: {e}", foreground='red')
        except Exception as e:
            self.widgets['test_status'].config(text=f"✗ Error: {str(e)[:30]}", foreground='red')

        # Update hardware status after test
        self.update_hardware_status()
    
    def on_sleep_timeout_changed(self, value):
        """Handle sleep timeout slider change"""
        if self.updating_from_config:
            return
        
        minutes = int(float(value))
        self.widgets['sleep_label'].config(text=f"{minutes} minute{'s' if minutes != 1 else ''}")
        self.on_setting_changed()
    

    def on_idle_timeout_changed(self, value):
        """Handle idle timeout slider change"""
        if self.updating_from_config:
            return
        
        timeout = float(value)
        self.widgets['idle_label'].config(text=f"{timeout:.1f} second{'s' if timeout != 1.0 else ''}")
        self.on_setting_changed()
    
    def update_slider_labels(self):
        """Update all slider labels with current values"""
        if 'sleep_label' in self.widgets:
            minutes = self.widgets['sleep_timeout'].get()
            self.widgets['sleep_label'].config(text=f"{minutes} minute{'s' if minutes != 1 else ''}")
        
        if 'sens_label' in self.widgets:
            sens = self.widgets['sensitivity'].get()
            self.widgets['sens_label'].config(text=f"{sens:.1f}x")
        
        if 'idle_label' in self.widgets:
            timeout = self.widgets['idle_timeout'].get()
            self.widgets['idle_label'].config(text=f"{timeout:.1f} second{'s' if timeout != 1.0 else ''}")
    
    def update_preview(self):
        """Update the preview text"""
        if 'preview_label' in self.widgets:
            if self.changes_made:
                self.widgets['preview_label'].config(text="● Settings modified - click Apply or Save to update", 
                                                    foreground='orange')
            else:
                self.widgets['preview_label'].config(text="Changes will be applied to your Bongo Cat display", 
                                                    foreground='gray')
    
    def update_status_info(self):
        """Update status information"""
        if 'status_label' in self.widgets and self.config:
            config_file = self.config.config_file
            status_text = f"Configuration file: {config_file}"
            self.widgets['status_label'].config(text=status_text)
    
    def update_hardware_status(self):
        """Update hardware monitoring status display"""
        if 'hardware_info' not in self.widgets:
            return
            
        if not self.engine:
            self.widgets['hardware_info'].config(text="Hardware monitoring: Engine not available")
            return
            
        hardware_status = self.engine.get_hardware_status()
        
        if hardware_status['enabled']:
            if hardware_status['available']:
                status_text = "Hardware monitoring: Active"
                temp_text = f"CPU: {hardware_status['cpu_temp']:.1f}°C  GPU: {hardware_status['gpu_temp']:.1f}°C"
            else:
                status_text = "Hardware monitoring: Enabled (Unavailable)"
                temp_text = "Check LibreHardwareMonitorLib.dll and Windows admin privileges"
        else:
            status_text = "Hardware monitoring: Disabled"
            temp_text = ""
            
        self.widgets['hardware_info'].config(text=status_text)
        if 'temp_display' in self.widgets:
            self.widgets['temp_display'].config(text=temp_text)
    
    def apply_settings(self):
        """Apply current settings without saving to file"""
        if not self.config:
            messagebox.showerror("Error", "No configuration manager available")
            return
        
        try:
            # Apply display settings
            self.config.set_setting('display', 'show_cpu', self.widgets['show_cpu'].get())
            self.config.set_setting('display', 'show_ram', self.widgets['show_ram'].get())
            self.config.set_setting('display', 'show_wpm', self.widgets['show_wpm'].get())
            self.config.set_setting('display', 'show_time', self.widgets['show_time'].get())
            self.config.set_setting('display', 'time_format_24h', self.widgets['time_format'].get() == '24')
            self.config.set_setting('display', 'show_cpu_temp', self.widgets['show_cpu_temp'].get())
            self.config.set_setting('display', 'show_gpu_temp', self.widgets['show_gpu_temp'].get())
            
            # Apply advanced settings
            self.config.set_setting('advanced', 'hardware_monitoring', self.widgets['hardware_monitoring'].get())
            self.config.set_setting('advanced', 'require_admin_for_cpu_temp', self.widgets['require_admin_for_cpu'].get())

            # Apply telemetry settings (new consent-based system)
            try:
                from . import settings as app_settings
                telemetry_cfg = app_settings.load()

                telemetry_cfg['telemetry']['hardware_monitoring_consented'] = self.widgets['hardware_consent'].get()
                telemetry_cfg['telemetry']['hardware_monitoring_enabled'] = self.widgets['hardware_monitoring'].get()
                telemetry_cfg['telemetry']['provider'] = self.widgets['hardware_provider'].get()
                telemetry_cfg['telemetry']['gpu_only'] = self.widgets['gpu_only'].get()

                app_settings.save(telemetry_cfg)

            except ImportError:
                print("⚠️ Settings module not available, telemetry settings not saved")
            
            # Apply behavior settings
            self.config.set_setting('behavior', 'sleep_timeout_minutes', self.widgets['sleep_timeout'].get())
    
            self.config.set_setting('behavior', 'idle_timeout_seconds', self.widgets['idle_timeout'].get())
            
            # Apply connection settings
            self.config.set_setting('connection', 'com_port', self.widgets['com_port'].get())
            self.config.set_setting('connection', 'baudrate', self.widgets['baudrate'].get())
            self.config.set_setting('connection', 'auto_reconnect', self.widgets['auto_reconnect'].get())
            self.config.set_setting('connection', 'timeout_seconds', self.widgets['conn_timeout'].get())
            
            # Apply startup settings
            self.config.set_setting('startup', 'start_with_windows', self.widgets['start_with_windows'].get())
            self.config.set_setting('startup', 'start_minimized', self.widgets['start_minimized'].get())
            self.config.set_setting('startup', 'show_notifications', self.widgets['show_notifications'].get())
            
            # Apply settings to Arduino immediately if engine is available
            if self.engine and hasattr(self.engine, 'apply_all_config_to_arduino'):
                try:
                    self.engine.apply_all_config_to_arduino()
                    print("✅ Settings applied to Arduino immediately")
                except Exception as e:
                    print(f"⚠️ Failed to apply settings to Arduino: {e}")
            
            self.changes_made = False
            self.update_preview()
            messagebox.showinfo("Success", "Settings applied successfully and sent to Arduino!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply settings: {e}")
    
    def save_settings(self):
        """Save current settings to file and Arduino"""
        self.apply_settings()
        
        if self.config:
            if self.config.save_config():
                # Also save to Arduino EEPROM if engine is available
                if self.engine and hasattr(self.engine, 'save_config_to_arduino'):
                    self.engine.save_config_to_arduino()
                    messagebox.showinfo("Success", "Settings saved to file and Arduino EEPROM!")
                else:
                    messagebox.showinfo("Success", "Settings saved to file!")
            else:
                messagebox.showerror("Error", "Failed to save settings to file")
    
    def cancel_settings(self):
        """Cancel changes and revert to original settings"""
        if self.changes_made:
            if messagebox.askyesno("Confirm", "Discard all changes?"):
                self.load_current_settings()
                self.changes_made = False
                self.update_preview()
        else:
            self.close_window()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Confirm", "Reset all settings to defaults?"):
            if self.config:
                self.config.reset_to_defaults()
                self.load_current_settings()
                self.changes_made = True
                self.update_preview()
                messagebox.showinfo("Reset", "Settings reset to defaults. Click Apply or Save to confirm.")
    
    def on_window_close(self):
        """Handle window close event"""
        try:
            if self.changes_made:
                result = messagebox.askyesnocancel("Unsaved Changes", 
                                                 "You have unsaved changes. Save before closing?")
                if result is True:  # Yes - save
                    self.save_settings()
                    self.close_window()
                elif result is False:  # No - discard
                    self.close_window()
                # Cancel - do nothing
            else:
                self.close_window()
        except Exception as e:
            print(f"❌ Error in window close handler: {e}")
            # Force close anyway
            self.close_window()
    
    def close_window(self):
        """Close the settings window"""
        try:
            if self.window:
                print("🗂️ Closing settings window...")
                self.window.destroy()
                self.window = None
                print("✅ Settings window closed")
            
            if self.on_close_callback:
                self.on_close_callback()
                
        except Exception as e:
            print(f"❌ Error closing window: {e}")
            # Force cleanup
            self.window = None
            if self.on_close_callback:
                try:
                    self.on_close_callback()
                except:
                    pass
    
    def show(self):
        """Show the settings window"""
        try:
            if not self.window or not self.window.winfo_exists():
                print("🔧 Creating new settings window...")
                self.create_window()
            else:
                print("🔧 Showing existing settings window...")
                # Reload settings for existing window
                self.load_current_settings()
            
            if self.window:
                # Show and focus the window
                self.window.deiconify()  # Make sure it's not minimized
                self.window.lift()
                self.window.focus_set()
                print("✅ Settings window displayed")
            else:
                print("❌ Failed to create settings window")
                
        except Exception as e:
            print(f"❌ Error showing settings window: {e}")
            if self.window:
                try:
                    self.window.destroy()
                except:
                    pass
                self.window = None

    def create_advanced_tab(self, notebook):
        """Create the advanced settings tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Advanced")
        
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Hardware monitoring section
        self._build_hardware_monitoring_section(main_frame)

    def _build_hardware_monitoring_section(self, parent):
        self._cfg = getattr(self, "_cfg", settings.load())

        # Bindable state
        self._hm_enabled_var = tk.BooleanVar(value=self._cfg["telemetry"]["hardware_monitoring_enabled"])
        self._gpu_only_var   = tk.BooleanVar(value=self._cfg["telemetry"]["gpu_only"])
        self._provider_var   = tk.StringVar(value=self._cfg["telemetry"]["provider"])

        # Toggle (gated by consent)
        def on_toggle():
            if self._hm_enabled_var.get():
                if not self._cfg["telemetry"]["hardware_monitoring_consented"]:
                    if not self._show_consent_once():
                        self._hm_enabled_var.set(False)
                        return
            self._cfg["telemetry"]["hardware_monitoring_enabled"] = self._hm_enabled_var.get()
            settings.save(self._cfg)

        # GPU-only
        def on_gpu_only():
            self._cfg["telemetry"]["gpu_only"] = self._gpu_only_var.get()
            settings.save(self._cfg)

        # Provider change
        def on_provider():
            self._cfg["telemetry"]["provider"] = self._provider_var.get()
            settings.save(self._cfg)

        # --- UI widgets ---
        frm = tk.LabelFrame(parent, text="Hardware Monitoring")
        frm.pack(fill="x", pady=6)

        tk.Checkbutton(
            frm, text="Enable hardware monitoring (requires consent)",
            variable=self._hm_enabled_var, command=on_toggle
        ).pack(anchor="w", padx=8, pady=4)

        tk.Checkbutton(
            frm, text="GPU-only (least privilege; recommended)",
            variable=self._gpu_only_var, command=on_gpu_only
        ).pack(anchor="w", padx=8, pady=2)

        row = tk.Frame(frm)
        tk.Label(row, text="Provider:").pack(side="left", padx=(8, 4))
        for p in ("auto", "lhm_http", "nvml"):
            tk.Radiobutton(row, text=p, value=p, variable=self._provider_var, command=on_provider)\
                .pack(side="left", padx=4)
        row.pack(anchor="w", pady=4)

        tk.Button(frm, text="Test sensors", command=self._test_sensors).pack(anchor="w", padx=8, pady=6)

    def _show_consent_once(self) -> bool:
        # One-time modal
        if self._cfg["telemetry"]["hardware_monitoring_consented"]:
            return True
        consent = tk.Toplevel(self.window)
        consent.title("Hardware Monitoring Consent")
        consent.grab_set()
        txt = (
            "This feature reads local hardware sensors (e.g., GPU/CPU temperature) "
            "to drive animations. By default, the app uses least-privilege methods "
            "(no admin rights). It may query a local LibreHardwareMonitor endpoint "
            "or GPU libraries. No data leaves your machine.\n\n"
            "Do you consent to enable hardware monitoring?"
        )
        msg = tk.Message(consent, text=txt, width=440)
        msg.pack(padx=12, pady=12)

        agreed = {"ok": False}
        def accept():
            agreed["ok"] = True
            self._cfg["telemetry"]["hardware_monitoring_consented"] = True
            settings.save(self._cfg)
            consent.destroy()
        def decline():
            consent.destroy()

        btns = tk.Frame(consent)
        tk.Button(btns, text="I Consent", command=accept).pack(side="left", padx=6)
        tk.Button(btns, text="Cancel", command=decline).pack(side="left", padx=6)
        btns.pack(pady=8)

        self.window.wait_window(consent)
        return agreed["ok"]

    def _test_sensors(self):
        try:
            data = read_sensors(self._cfg)
            msg = f"Sensor probe OK:\n{data}"
        except Exception as e:
            msg = f"Sensor probe failed:\n{e}"

        # Helpful hints
        if self._provider_var.get() in ("auto", "lhm_http"):
            msg += "\n\nTip: If using LibreHardwareMonitor, open it and enable " \
                   "'Options → Remote Web Server' (default http://localhost:8085)."
        msg += "\n\nNote: App is {}elevated.".format("" if is_admin_windows() else "NOT ")

        messagebox.showinfo("Test sensors", msg)

def main():
    """Test the settings GUI independently"""
    from config import ConfigManager
    
    print("🧪 Testing Settings GUI...")
    
    # Create config manager
    config = ConfigManager()
    
    # Create and show GUI (no engine for standalone testing)
    gui = BongoCatSettingsGUI(config_manager=config, engine=None)
    gui.show()
    
    # Run main loop
    if gui.window:
        gui.window.mainloop()
    
    print("✅ Settings GUI test completed")

if __name__ == "__main__":
    main()
