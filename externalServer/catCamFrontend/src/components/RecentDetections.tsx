import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Eye, Download } from "lucide-react";

const recentDetections = [
  {
    id: 1,
    timestamp: "14:32:15",
    confidence: 98,
    category: "Cat Present",
    duration: "2m 15s",
    thumbnail: "🐱"
  },
  {
    id: 2,
    timestamp: "14:28:42",
    confidence: 87,
    category: "Cat Playing", 
    duration: "1m 32s",
    thumbnail: "🐱"
  },
  {
    id: 3,
    timestamp: "14:15:08",
    confidence: 95,
    category: "Cat Sleeping",
    duration: "15m 22s", 
    thumbnail: "🐱"
  },
  {
    id: 4,
    timestamp: "13:58:33",
    confidence: 92,
    category: "Cat Present",
    duration: "3m 8s",
    thumbnail: "🐱"
  },
  {
    id: 5,
    timestamp: "13:45:17",
    confidence: 76,
    category: "Unknown Object",
    duration: "45s",
    thumbnail: "❓"
  }
];

export function RecentDetections() {
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return "bg-green-500";
    if (confidence >= 75) return "bg-yellow-500";
    return "bg-red-500";
  };

  const getCategoryVariant = (category: string) => {
    switch (category) {
      case "Cat Present": return "default";
      case "Cat Playing": return "secondary";
      case "Cat Sleeping": return "outline";
      default: return "destructive";
    }
  };

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Recent Detections</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {recentDetections.map((detection) => (
            <div key={detection.id} className="flex items-center justify-between p-3 border rounded-lg">
              <div className="flex items-center gap-3">
                <div className="text-2xl">{detection.thumbnail}</div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{detection.timestamp}</span>
                    <Badge variant={getCategoryVariant(detection.category)}>
                      {detection.category}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <span>Duration: {detection.duration}</span>
                    <span>•</span>
                    <div className="flex items-center gap-1">
                      <div className={`w-2 h-2 rounded-full ${getConfidenceColor(detection.confidence)}`}></div>
                      <span>{detection.confidence}% confidence</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm">
                  <Eye className="w-4 h-4" />
                </Button>
                <Button variant="outline" size="sm">
                  <Download className="w-4 h-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
        
        <Button variant="outline" className="w-full mt-4">
          View All Detections
        </Button>
      </CardContent>
    </Card>
  );
}