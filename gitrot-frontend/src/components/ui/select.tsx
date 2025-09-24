import * as React from "react";
import { ChevronDown, Check } from "lucide-react";
import { cn } from "@/lib/utils";

export interface SelectOption {
  value: string;
  label: string;
  description?: string;
  badge?: string;
  cost?: string;
  icon?: string;
  recommended?: boolean;
}

export interface SelectProps {
  options: SelectOption[];
  value: string;
  onValueChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  label?: string;
}

const Select = React.forwardRef<HTMLButtonElement, SelectProps>(
  (
    {
      options,
      value,
      onValueChange,
      placeholder = "Select an option...",
      disabled = false,
      className,
      label,
      ...props
    },
    ref
  ) => {
    const [isOpen, setIsOpen] = React.useState(false);
    const selectedOption = options.find((option) => option.value === value);

    const handleSelect = (optionValue: string) => {
      onValueChange(optionValue);
      setIsOpen(false);
    };

    return (
      <div className="relative w-full">
        {label && (
          <label className="text-sm font-medium text-stone-700 mb-2 block">
            {label}
          </label>
        )}
        <div className="relative">
          <button
            ref={ref}
            type="button"
            onClick={() => setIsOpen(!isOpen)}
            disabled={disabled}
            className={cn(
              "w-full min-h-[3rem] px-3 py-2 text-left bg-white border border-stone-200 rounded-lg",
              "hover:border-stone-300 focus:outline-none focus:ring-2 focus:ring-stone-400 focus:border-stone-400",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              "transition-all duration-200 ease-in-out",
              className
            )}
            {...props}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3 flex-1 min-w-0">
                {selectedOption ? (
                  <>
                    {selectedOption.icon && (
                      <span className="text-lg flex-shrink-0">
                        {selectedOption.icon}
                      </span>
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-stone-900 truncate">
                          {selectedOption.label}
                        </span>
                        {selectedOption.recommended && (
                          <span className="px-1.5 py-0.5 text-xs font-medium bg-green-100 text-green-700 rounded-full flex-shrink-0">
                            ✓
                          </span>
                        )}
                        {selectedOption.badge &&
                          !selectedOption.recommended && (
                            <span className="px-1.5 py-0.5 text-xs font-medium bg-blue-100 text-blue-700 rounded-full flex-shrink-0">
                              {selectedOption.badge}
                            </span>
                          )}
                      </div>
                      {selectedOption.description && (
                        <p className="text-xs text-stone-500 truncate mt-0.5">
                          {selectedOption.description}
                        </p>
                      )}
                    </div>
                  </>
                ) : (
                  <span className="text-sm text-stone-500">{placeholder}</span>
                )}
              </div>
              <ChevronDown
                className={cn(
                  "h-4 w-4 text-stone-400 transition-transform duration-200 flex-shrink-0",
                  isOpen && "transform rotate-180"
                )}
              />
            </div>
          </button>

          {isOpen && (
            <>
              {/* Backdrop to close dropdown when clicking outside */}
              <div
                className="fixed inset-0 z-40"
                onClick={() => setIsOpen(false)}
              />

              <div className="absolute z-50 w-full mt-1 bg-white border border-stone-200 rounded-lg shadow-lg max-h-60 overflow-auto">
                {options.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => handleSelect(option.value)}
                    className={cn(
                      "w-full px-3 py-3 text-left hover:bg-stone-50 focus:bg-stone-50 focus:outline-none",
                      "transition-colors duration-150 ease-in-out border-b border-stone-100 last:border-b-0",
                      "first:rounded-t-lg last:rounded-b-lg",
                      value === option.value && "bg-stone-100"
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3 flex-1 min-w-0">
                        {option.icon && (
                          <span className="text-lg flex-shrink-0">
                            {option.icon}
                          </span>
                        )}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="text-sm font-medium text-stone-900 truncate">
                              {option.label}
                            </span>
                            {option.recommended && (
                              <span className="px-2 py-0.5 text-xs font-medium bg-green-100 text-green-700 rounded-full flex-shrink-0">
                                ✓ Recommended
                              </span>
                            )}
                            {option.badge && !option.recommended && (
                              <span className="px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-700 rounded-full flex-shrink-0">
                                {option.badge}
                              </span>
                            )}
                          </div>
                          {option.description && (
                            <p className="text-xs text-stone-500 line-clamp-2 mb-1">
                              {option.description}
                            </p>
                          )}
                          {option.cost && (
                            <div className="flex items-center space-x-2 mt-1">
                              <span className="text-xs text-stone-400">
                                Cost: {option.cost}
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                      {value === option.value && (
                        <Check className="h-4 w-4 text-green-600 flex-shrink-0" />
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    );
  }
);

Select.displayName = "Select";

export { Select };
