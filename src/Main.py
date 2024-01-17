import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider, QFileDialog, QStyle
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtGui import QFont
from SampleClass import Sample 
import threading
import time

class SamplerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SMPL-HLPR")
        self.setGeometry(100, 100, 600, 450)  # x, y, width, height

        self.sample = None
        self.last_pitch_value = 0
        self.last_dir = ''

        self.initUI()


#---------------
# UI 
#---------------

    def initUI(self):
        # apply dark theme styles
        self.setStyleSheet("""
            QWidget {
                color: #b1b1b1;
                background-color: #323232;
            }
            QLabel {
                border: 2px solid #444;
                border-radius: 5px;
                background-color: #000;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12pt;
            }
            QPushButton {
                border: 1px solid #444;
                border-radius: 5px;
                padding: 5px;
                font-size: 12pt;
                background-color: #555;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QPushButton:pressed {
                background-color: #777;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999;
                height: 8px;
                background: #3C3C3C;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #FFF;
                border: 1px solid #DDD;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QSlider::add-page:horizontal {
                background: #575757;
            }
            QSlider::sub-page:horizontal {
                background: #2875C9;
            }
        """)

        # main widget and layout
        self.setFixedSize(965, 500)
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # left pannel (file loading, LCD)
        left_panel = QVBoxLayout()
        
        # LCD-
        self.track_info_display = QLabel("No file loaded\n\n\n")
        self.track_info_display.setAlignment(Qt.AlignCenter)
        self.track_info_display.setFixedSize(300, 300)  # Set a fixed size (width, height)
        left_panel.addWidget(self.track_info_display)

         # load 
        load_button = QPushButton("Load")
        load_button.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        load_button.setFixedSize(300, 40)  # Make the button larger
        load_button.clicked.connect(self.load_audio)
        left_panel.addWidget(load_button)

        # save 
        save_button = QPushButton("Save Audio")
        save_button.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        save_button.setFixedSize(300, 40)  # Make the button larger
        save_button.clicked.connect(self.save_audio)
        left_panel.addWidget(save_button)

        left_panel.addStretch()

        # right pannel (controls)
        right_panel = QVBoxLayout()

        # bit depth
        self.bit_depth_slider = self.create_slider(1, 16, 16, 'Bit Depth')
        self.bit_depth_value_label = QLabel('Bit Depth: 16')  # Initial value label for bit depth
        self.bit_depth_slider.valueChanged.connect(lambda: self.bit_depth_value_label.setText(f'Bit Depth: {self.bit_depth_slider.value()}'))
        self.bit_depth_slider.sliderReleased.connect(self.apply_changes)
        right_panel.addWidget(self.bit_depth_slider)
        right_panel.addWidget(self.bit_depth_value_label)

        # sample rate
        self.sample_rate_slider = self.create_slider(1000, 48000, 44100, 'Sample Rate')
        self.sample_rate_value_label = QLabel('Sample Rate: 44100')  # Initial value label for sample rate
        self.sample_rate_slider.valueChanged.connect(lambda: self.sample_rate_value_label.setText(f'Sample Rate: {self.sample_rate_slider.value()}'))
        self.sample_rate_slider.sliderReleased.connect(self.apply_changes)
        right_panel.addWidget(self.sample_rate_slider)
        right_panel.addWidget(self.sample_rate_value_label)

        # pitch
        self.pitch_slider = self.create_slider(-12, 12, 0, 'Pitch')
        self.pitch_value_label = QLabel('Pitch: 0')  # Initial value label for pitch
        self.pitch_slider.valueChanged.connect(lambda: self.pitch_value_label.setText(f'Pitch: {self.pitch_slider.value()}'))
        self.pitch_slider.sliderReleased.connect(self.apply_changes)
        right_panel.addWidget(self.pitch_slider)
        right_panel.addWidget(self.pitch_value_label)



        playback_layout = QHBoxLayout()

        # play
        play_button = QPushButton()
        play_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        play_button.setIcon(play_icon)
        play_button.setFixedSize(70, 60)  # Set a fixed size for the button
        play_button.clicked.connect(self.play_audio)
        playback_layout.addWidget(play_button)

        # pause
        pause_button = QPushButton()
        pause_icon = self.style().standardIcon(QStyle.SP_MediaPause)
        pause_button.setIcon(pause_icon)
        pause_button.setFixedSize(70, 60)  # Set a fixed size for the button
        pause_button.clicked.connect(self.stop_audio)
        playback_layout.addWidget(pause_button)

        # add the playback layout to the right panel
        right_panel.addLayout(playback_layout)

        # combine layouts
        main_layout.addLayout(left_panel)
        main_layout.addLayout(right_panel)

    def create_slider(self, min_value, max_value, initial_value, label):
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_value)
        slider.setMaximum(max_value)
        slider.setValue(initial_value)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(int((max_value - min_value) / 10))
        slider.setToolTip(label)
        return slider

    def reset_sliders(self):
        self.bit_depth_slider.setValue(16)
        self.sample_rate_slider.setValue(44100)
        self.pitch_slider.setValue(0)

        # Update labels
        self.bit_depth_value_label.setText('Bit Depth: 16')
        self.sample_rate_value_label.setText('Sample Rate: 44100')
        self.pitch_value_label.setText('Pitch: 0')


#---------------
# Backend
#---------------

    def load_audio(self):
        try:
            if self.sample:
                self.sample.stop_audio()

            start_directory = self.last_dir or QDir.homePath()
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Audio File", start_directory, "Audio Files (*.wav *.mp3 *.m4a)")

            if file_path:
                self.sample = Sample(file_path)
                self.reset_sliders()
                track_info_text = (f"Loaded: {file_path.split('/')[-1]}\n"
                                   f"Sample Rate: {self.sample.sample_rate} Hz\n"
                                   f"Length: {len(self.sample.audio_array) / self.sample.sample_rate} seconds\n"
                                   f"Channels: {'Stereo' if self.sample.audio_array.ndim > 1 and self.sample.audio_array.shape[1] == 2 else 'Mono'}")
                self.track_info_display.setText(track_info_text)
                self.last_dir = QDir(file_path).dirName()
        except Exception as e:
            print(f"Error loading audio file: {e}")

    def play_audio(self):
        if self.sample:
            threading.Thread(target=self.sample.play_audio, daemon=True).start()

    def stop_audio(self):
        if self.sample:
            self.sample.stop_audio()

    def save_audio(self):
        if self.sample:
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Audio", "", "Audio Files (*.wav)")
            if save_path:
                self.sample.save_audio(save_path)

    def apply_changes(self):
        if self.sample:
            threading.Thread(target=self.apply_audio_changes, daemon=True).start()

    def apply_pitch_change(self):
        if self.sample:
            new_pitch = self.pitch_slider.value()
            self.last_pitch_value = new_pitch
            self.sample.change_pitch(new_pitch)


    def apply_audio_changes(self):
        bit_depth = self.bit_depth_slider.value()
        sample_rate = self.sample_rate_slider.value()
        self.sample.stop_audio()
        time.sleep(0.1)
        self.apply_pitch_change()
        time.sleep(0.1)
        self.sample.change_bit_depth(bit_depth)
        time.sleep(0.1)
        self.sample.change_sample_rate(sample_rate)
        time.sleep(0.1)
        time.sleep(0.1)
        self.sample.play_audio()


#---------------
# Main
#---------------

class main:
    def __init__(self):
        app = QApplication(sys.argv)
        ex = SamplerApp()
        ex.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()

