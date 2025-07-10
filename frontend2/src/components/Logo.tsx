
const Logo = () => {
  return (
    <div className="flex items-center gap-2">
      <div className="h-10 w-32 rounded-md bg-primary flex items-center justify-center gap-2 px-2">
        {/* Little Robot Icon */}
        <div className="h-5 w-5 text-primary-foreground">
          <svg viewBox="0 0 24 24" fill="currentColor" className="w-full h-full">
            <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 7.5V9C15 10.1 14.1 11 13 11V13H16L18.5 18H21V20H3V18H5.5L8 13H11V11C9.9 11 9 10.1 9 9V7.5L3 7V9H1V5H3L9 5.5C9 5.5 9 5.3 9 5C9 3.3 10.3 2 12 2S15 3.3 15 5C15 5.3 15 5.5 15 5.5L21 5H23V9H21Z"/>
          </svg>
        </div>
        
        {/* Divert.ai Text */}
        <span className="text-sm font-bold text-primary-foreground whitespace-nowrap">
          Divert.ai
        </span>
      </div>
    </div>
  );
};

export default Logo;