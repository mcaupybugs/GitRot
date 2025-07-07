import { Sparkles } from "lucide-react";

export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center">
      <div className="relative">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-stone-900"></div>
        <Sparkles className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 h-4 w-4 text-stone-900 animate-pulse" />
      </div>
    </div>
  );
}
