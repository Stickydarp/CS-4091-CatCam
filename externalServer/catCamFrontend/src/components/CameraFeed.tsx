import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Play, Pause, RotateCcw, ZoomIn, ZoomOut, Volume2 } from "lucide-react";
import { useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { toast } from "sonner";

export function CameraFeed() {
  const [isPlaying, setIsPlaying] = useState(true);
  const [isDetectionActive, setIsDetectionActive] = useState(true);
  const [isPlayingSound, setIsPlayingSound] = useState(false);

  const playCatSound = (soundType: string) => {
    setIsPlayingSound(true);
    toast.success(`Playing ${soundType} sound...`, {
      description: "Cat sound is being played through the system speaker",
    });
    
    // Simulate sound playing for 2 seconds
    setTimeout(() => {
      setIsPlayingSound(false);
    }, 2000);
  };

  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle>Live Camera Feed</CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant={isDetectionActive ? "default" : "secondary"}>
              AI Detection: {isDetectionActive ? "Active" : "Inactive"}
            </Badge>
            <Badge variant="outline">
              Status: {isPlaying ? "Live" : "Paused"}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Mock Camera Feed */}
        <div className="relative bg-gray-900 rounded-lg overflow-hidden aspect-video">
          <div className="absolute inset-0 bg-gradient-to-br from-gray-800 to-gray-900 flex items-center justify-center">
            <div className="text-center space-y-2">
              <div className="w-20 h-20 mx-auto bg-gray-700 rounded-full flex items-center justify-center">
                <div className="w-8 h-8 bg-green-500 rounded-full animate-pulse"></div>
              </div>
              <p className="text-white opacity-75">Camera Feed</p>
              <p className="text-green-400 text-sm">● LIVE</p>
            </div>
          </div>
          
          {/* Detection Overlay */}
          {isDetectionActive && (
            <div className="absolute top-4 left-4 space-y-2">
              <div className="bg-green-500/90 text-white px-2 py-1 rounded text-sm">
                Cat Detected
              </div>
              <div className="border-2 border-green-500 w-32 h-24 rounded"></div>
            </div>
          )}
          
          {/* Timestamp */}
          <div className="absolute bottom-4 right-4 bg-black/50 text-white px-2 py-1 rounded text-sm">
            {new Date().toLocaleTimeString()}
          </div>
        </div>

        {/* Camera Controls */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => setIsPlaying(!isPlaying)}
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              {isPlaying ? "Pause" : "Play"}
            </Button>
            <Button variant="outline" size="sm">
              <RotateCcw className="w-4 h-4" />
              Restart
            </Button>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button 
                  variant="outline" 
                  size="sm"
                  disabled={isPlayingSound}
                >
                  <Volume2 className="w-4 h-4" />
                  {isPlayingSound ? "Playing..." : "Cat Sounds"}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start">
                <DropdownMenuItem onClick={() => playCatSound("Meow")}>
                  🐱 Play Meow
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => playCatSound("Purr")}>
                  😸 Play Purr
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => playCatSound("Hiss")}>
                  😾 Play Hiss
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => playCatSound("Chirp")}>
                  😺 Play Chirp
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
          
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <ZoomOut className="w-4 h-4" />
            </Button>
            <span className="text-sm text-muted-foreground">100%</span>
            <Button variant="outline" size="sm">
              <ZoomIn className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}