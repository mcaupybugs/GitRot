"use client";

import dynamic from "next/dynamic";
import { SelectProps } from "./select";

// Dynamically import Select with no SSR
const SelectComponent = dynamic(
  () => import("./select").then((mod) => ({ default: mod.Select })),
  {
    ssr: false,
    loading: () => (
      <div className="space-y-2">
        <div className="text-sm font-medium text-stone-700">Loading...</div>
        <div className="w-full min-h-[3rem] px-3 py-2 bg-stone-100 border border-stone-200 rounded-lg animate-pulse">
          <div className="flex items-center space-x-3">
            <div className="w-6 h-6 bg-stone-300 rounded-full"></div>
            <div className="flex-1">
              <div className="w-20 h-4 bg-stone-300 rounded mb-1"></div>
              <div className="w-32 h-3 bg-stone-300 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    ),
  }
);

export const ClientSelect = (props: SelectProps) => {
  return <SelectComponent {...props} />;
};
