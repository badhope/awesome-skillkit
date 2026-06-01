import * as React from "react";
import { cn } from "@/lib/utils";
import { X } from "lucide-react";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  icon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  clearable?: boolean;
  onClear?: () => void;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, error, icon, rightIcon, clearable, onClear, value, ...props }, ref) => {
    const [internalValue, setInternalValue] = React.useState(value ?? "");
    const inputRef = React.useRef<HTMLInputElement | null>(null);
    const mergedRef = (node: HTMLInputElement | null) => {
      inputRef.current = node;
      if (typeof ref === "function") ref(node);
      else if (ref) (ref as React.MutableRefObject<HTMLInputElement | null>).current = node;
    };

    const displayValue = value !== undefined ? String(value) : internalValue;
    const showClear = clearable && !!displayValue;

    const handleClear = () => {
      setInternalValue("");
      onClear?.();
      if (inputRef.current) {
        inputRef.current.focus();
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
          window.HTMLInputElement.prototype,
          "value"
        )?.set;
        if (nativeInputValueSetter) {
          nativeInputValueSetter.call(inputRef.current, "");
          inputRef.current.dispatchEvent(new Event("input", { bubbles: true }));
        }
      }
    };

    return (
      <div className="relative w-full">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none">
            {icon}
          </div>
        )}
        <input
          type={type}
          className={cn(
            "flex h-11 w-full rounded-lg border border-input bg-background px-3 py-2 text-base ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors duration-200 sm:h-10 sm:text-sm",
            icon && "pl-10",
            (rightIcon || showClear) && "pr-10",
            error && "border-destructive focus-visible:ring-destructive",
            className
          )}
          ref={mergedRef}
          value={displayValue}
          onChange={(e) => {
            setInternalValue(e.target.value);
          }}
          {...props}
        />
        {showClear && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full p-0.5 text-muted-foreground hover:text-foreground transition-colors touch-manipulation min-h-[28px] min-w-[28px] flex items-center justify-center"
            aria-label="Clear input"
          >
            <X className="h-4 w-4" />
          </button>
        )}
        {!showClear && rightIcon && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none">
            {rightIcon}
          </div>
        )}
        {error && <p className="mt-1 text-xs text-destructive">{error}</p>}
      </div>
    );
  }
);
Input.displayName = "Input";

export { Input };
