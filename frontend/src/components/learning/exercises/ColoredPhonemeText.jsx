export const ColoredPhonemeText = ({ text, colorMap, className = "" }) => {
  if (!text) return null;
  
  return (
    <span className={`font-opendyslexic ${className}`}>
      {text.split('').map((char, index) => {
        const color = colorMap[char.toLowerCase()] || 'inherit';
        return (
          <span key={index} style={{ color }}>
            {char}
          </span>
        );
      })}
    </span>
  );
};
