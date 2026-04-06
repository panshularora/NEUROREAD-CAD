import { useState, useCallback, useEffect } from 'react';
import { motion } from 'framer-motion';
import { debounce } from 'lodash';
import { DndContext, useDraggable, useDroppable, closestCenter } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import { useMultimodalTTS } from '../../../hooks/useMultimodalTTS';

function Tile({ id, letter, color, size }) {
  const { attributes, listeners, setNodeRef, transform } = useDraggable({ id });
  const style = {
    transform: CSS.Translate.toString(transform),
    backgroundColor: color === 'neutral' ? '#4A4A4A' : color, 
    width: `${size}px`,
    height: `${size}px`,
  };

  return (
    <div ref={setNodeRef} style={style} {...listeners} {...attributes}
         className="rounded-xl shadow-lg flex items-center justify-center font-opendyslexic text-white text-4xl font-bold cursor-grab active:cursor-grabbing hover:scale-105 transition-transform z-10">
      {letter}
    </div>
  );
}

function DropZone({ id, currentLetter }) {
  const { setNodeRef, isOver } = useDroppable({ id });
  return (
    <div ref={setNodeRef} className={`w-20 h-24 border-4 border-dashed rounded-xl flex items-center justify-center ${isOver ? 'border-moss bg-moss/20' : 'border-cream/30'}`}>
      {currentLetter && (
        <div className="font-opendyslexic font-bold text-4xl text-cream">{currentLetter}</div>
      )}
    </div>
  );
}

export default function ConstructionExercise({ data, onSubmit, modality }) {
  const [startTime] = useState(Date.now());
  const { playTTS } = useMultimodalTTS(modality);
  
  const [tiles, setTiles] = useState([]);
  const [slots, setSlots] = useState([]);

  useEffect(() => {
    if (modality.tile_layout) {
      setTiles(modality.tile_layout.map((t, i) => ({ ...t, id: `tile-${i}` })));
    }
    if (data.correct_answer) {
      setSlots(Array(data.correct_answer.length).fill(null));
    }
  }, [modality, data]);

  const handleDragEnd = (event) => {
    const { active, over } = event;
    if (over && over.id.startsWith('slot-')) {
      const slotIndex = parseInt(over.id.replace('slot-', ''), 10);
      const draggedTile = tiles.find(t => t.id === active.id);
      
      const newSlots = [...slots];
      newSlots[slotIndex] = draggedTile.letter;
      setSlots(newSlots);
      
      // Auto-submit if all slots filled
      if (newSlots.every(s => s !== null)) {
        const answer = newSlots.join('');
        submitAnswer(answer);
      }
    }
  };

  const submitAnswer = useCallback(debounce((answer) => {
    const timeMs = Date.now() - startTime;
    onSubmit(answer, timeMs);
  }, 500), [startTime, onSubmit]);

  return (
    <div className="flex flex-col items-center justify-center w-full max-w-4xl py-12">
       <button onClick={playTTS} className="mb-12 w-16 h-16 rounded-full bg-cream/10 flex items-center justify-center hover:bg-cream/20">
        <span className="iconify text-3xl text-cream" data-icon="solar:volume-loud-bold" />
      </button>

      <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        {/* Drop Zones */}
        <div className="flex gap-4 mb-16">
          {slots.map((letter, idx) => (
            <DropZone key={idx} id={`slot-${idx}`} currentLetter={letter} />
          ))}
        </div>

        {/* Draggable Bank */}
        <div className="flex flex-wrap gap-6 justify-center max-w-2xl bg-cream/5 p-8 rounded-[2rem]">
          {tiles.map((tile) => (
            <Tile key={tile.id} id={tile.id} letter={tile.letter} color={tile.color} size={64} />
          ))}
        </div>
      </DndContext>
    </div>
  );
}
