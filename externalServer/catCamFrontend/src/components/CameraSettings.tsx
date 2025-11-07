import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Switch } from "./ui/switch";
import { Slider } from "./ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Label } from "./ui/label";
import { Settings, Camera, Brain, Bell } from "lucide-react";
import { useState } from "react";

export function CameraSettings() {
  const [aiDetectionEnabled, setAiDetectionEnabled] = useState(true);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [sensitivity, setSensitivity] = useState([75]);
  const [recordingEnabled, setRecordingEnabled] = useState(false);

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings className="w-5 h-5" />
          Camera Settings
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* AI Detection Settings */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Brain className="w-4 h-4" />
            <Label className="font-medium">AI Detection</Label>
          </div>
          
          <div className="space-y-3 pl-6">
            <div className="flex items-center justify-between">
              <Label htmlFor="ai-detection">Enable AI Detection</Label>
              <Switch 
                id="ai-detection"
                checked={aiDetectionEnabled}
                onCheckedChange={setAiDetectionEnabled}
              />
            </div>
            
            <div className="space-y-2">
              <Label>Detection Sensitivity</Label>
              <Slider
                value={sensitivity}
                onValueChange={setSensitivity}
                max={100}
                min={1}
                step={1}
                disabled={!aiDetectionEnabled}
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Low</span>
                <span>{sensitivity[0]}%</span>
                <span>High</span>
              </div>
            </div>
            
            <div className="space-y-2">
              <Label>Detection Model</Label>
              <Select defaultValue="standard">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="standard">Standard Model</SelectItem>
                  <SelectItem value="high-accuracy">High Accuracy Model</SelectItem>
                  <SelectItem value="fast">Fast Detection Model</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        {/* Camera Settings */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Camera className="w-4 h-4" />
            <Label className="font-medium">Camera</Label>
          </div>
          
          <div className="space-y-3 pl-6">
            <div className="space-y-2">
              <Label>Resolution</Label>
              <Select defaultValue="1080p">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="720p">720p HD</SelectItem>
                  <SelectItem value="1080p">1080p Full HD</SelectItem>
                  <SelectItem value="4k">4K Ultra HD</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label>Frame Rate</Label>
              <Select defaultValue="30fps">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="15fps">15 FPS</SelectItem>
                  <SelectItem value="30fps">30 FPS</SelectItem>
                  <SelectItem value="60fps">60 FPS</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex items-center justify-between">
              <Label htmlFor="recording">Auto Recording</Label>
              <Switch 
                id="recording"
                checked={recordingEnabled}
                onCheckedChange={setRecordingEnabled}
              />
            </div>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Bell className="w-4 h-4" />
            <Label className="font-medium">Notifications</Label>
          </div>
          
          <div className="space-y-3 pl-6">
            <div className="flex items-center justify-between">
              <Label htmlFor="notifications">Enable Notifications</Label>
              <Switch 
                id="notifications"
                checked={notificationsEnabled}
                onCheckedChange={setNotificationsEnabled}
              />
            </div>
            
            <div className="space-y-2">
              <Label>Notification Types</Label>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="cat-detected" className="text-sm">Cat Detected</Label>
                  <Switch id="cat-detected" defaultChecked disabled={!notificationsEnabled} />
                </div>
                <div className="flex items-center justify-between">
                  <Label htmlFor="motion-detected" className="text-sm">Motion Detected</Label>
                  <Switch id="motion-detected" disabled={!notificationsEnabled} />
                </div>
                <div className="flex items-center justify-between">
                  <Label htmlFor="low-accuracy" className="text-sm">Low Accuracy Alert</Label>
                  <Switch id="low-accuracy" defaultChecked disabled={!notificationsEnabled} />
                </div>
              </div>
            </div>
          </div>
        </div>

        <Button className="w-full">
          Save Settings
        </Button>
      </CardContent>
    </Card>
  );
}