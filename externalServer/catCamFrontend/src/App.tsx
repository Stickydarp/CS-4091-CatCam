import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { CameraFeed } from "./components/CameraFeed";
import { AIMetrics } from "./components/AIMetrics";
import { RecentDetections } from "./components/RecentDetections";
import { CameraSettings } from "./components/CameraSettings";
import { Camera, BarChart3, Clock, Settings } from "lucide-react";
import { Toaster } from "./components/ui/sonner";

export default function App() {
  return (
    <div className="min-h-screen bg-background p-4">
      <Toaster />
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="space-y-2">
          <h1 className="text-3xl font-bold">Cat Camera Monitor</h1>
          <p className="text-muted-foreground">
            Monitor your cat's activity with AI-powered detection and analytics
          </p>
        </div>

        {/* Main Dashboard */}
        <Tabs defaultValue="monitor" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="monitor" className="flex items-center gap-2">
              <Camera className="w-4 h-4" />
              Monitor
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Analytics
            </TabsTrigger>
            <TabsTrigger value="history" className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              History
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Settings
            </TabsTrigger>
          </TabsList>

          <TabsContent value="monitor" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]">
              <div className="lg:col-span-2">
                <CameraFeed />
              </div>
              <div>
                <RecentDetections />
              </div>
            </div>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <AIMetrics />
          </TabsContent>

          <TabsContent value="history" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <RecentDetections />
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Detection Timeline</h3>
                <p className="text-muted-foreground">
                  Detailed history and timeline features would be implemented here, 
                  showing a chronological view of all cat detections with filtering 
                  and search capabilities.
                </p>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="settings" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <CameraSettings />
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">System Status</h3>
                <div className="grid grid-cols-1 gap-4">
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between">
                      <span>Camera Connection</span>
                      <span className="text-green-600">● Connected</span>
                    </div>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between">
                      <span>AI Model Status</span>
                      <span className="text-green-600">● Active</span>
                    </div>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between">
                      <span>Storage Space</span>
                      <span className="text-muted-foreground">2.4GB / 10GB</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}