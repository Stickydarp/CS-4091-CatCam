import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts";

const detectionData = [
  { time: "09:00", detections: 12, accuracy: 94 },
  { time: "10:00", detections: 8, accuracy: 96 },
  { time: "11:00", detections: 15, accuracy: 91 },
  { time: "12:00", detections: 22, accuracy: 98 },
  { time: "13:00", detections: 18, accuracy: 95 },
  { time: "14:00", detections: 25, accuracy: 97 },
  { time: "15:00", detections: 14, accuracy: 93 },
];

const accuracyData = [
  { day: "Mon", accuracy: 94 },
  { day: "Tue", accuracy: 96 },
  { day: "Wed", accuracy: 92 },
  { day: "Thu", accuracy: 98 },
  { day: "Fri", accuracy: 95 },
  { day: "Sat", accuracy: 97 },
  { day: "Sun", accuracy: 93 },
];

export function AIMetrics() {
  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Total Detections</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-semibold">1,247</div>
            <p className="text-xs text-muted-foreground">+12% from yesterday</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Average Accuracy</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-semibold">95.6%</div>
            <p className="text-xs text-muted-foreground">+2.1% improvement</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">False Positives</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-semibold">23</div>
            <p className="text-xs text-muted-foreground">-5% from last week</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Model Status</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge variant="default" className="bg-green-500">
              Optimal
            </Badge>
            <p className="text-xs text-muted-foreground mt-1">Last updated 2h ago</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Hourly Detection Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={detectionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Bar yAxisId="left" dataKey="detections" fill="hsl(var(--chart-1))" />
                <Line 
                  yAxisId="right" 
                  type="monotone" 
                  dataKey="accuracy" 
                  stroke="hsl(var(--chart-2))" 
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Weekly Accuracy Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={accuracyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis domain={[90, 100]} />
                <Tooltip />
                <Bar dataKey="accuracy" fill="hsl(var(--chart-3))" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Detection Categories */}
      <Card>
        <CardHeader>
          <CardTitle>Detection Categories</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center space-y-2">
              <div className="text-2xl font-semibold text-blue-600">892</div>
              <p className="text-sm text-muted-foreground">Cat Present</p>
            </div>
            <div className="text-center space-y-2">
              <div className="text-2xl font-semibold text-green-600">245</div>
              <p className="text-sm text-muted-foreground">Cat Playing</p>
            </div>
            <div className="text-center space-y-2">
              <div className="text-2xl font-semibold text-orange-600">87</div>
              <p className="text-sm text-muted-foreground">Cat Sleeping</p>
            </div>
            <div className="text-center space-y-2">
              <div className="text-2xl font-semibold text-red-600">23</div>
              <p className="text-sm text-muted-foreground">Unknown Object</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}