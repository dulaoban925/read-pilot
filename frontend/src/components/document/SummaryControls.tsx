/**
 * 摘要控制组件
 * 提供生成摘要、选择摘要深度等控制功能
 */
'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select';
import { Sparkles, RefreshCw } from 'lucide-react';

export interface SummaryControlsProps {
  /** 是否正在生成摘要 */
  isGenerating: boolean;
  /** 是否已存在摘要 */
  hasSummary: boolean;
  /** 当前摘要深度 */
  currentDepth?: 'brief' | 'detailed';
  /** 生成摘要回调 */
  onGenerate: (depth: 'brief' | 'detailed') => void;
  /** 重新生成摘要回调 */
  onRegenerate?: (depth: 'brief' | 'detailed') => void;
  /** 自定义类名 */
  className?: string;
}

export const SummaryControls: React.FC<SummaryControlsProps> = ({
  isGenerating,
  hasSummary,
  currentDepth = 'brief',
  onGenerate,
  onRegenerate,
  className = '',
}) => {
  const [selectedDepth, setSelectedDepth] = useState<'brief' | 'detailed'>(currentDepth);

  const handleGenerate = () => {
    if (hasSummary && onRegenerate) {
      onRegenerate(selectedDepth);
    } else {
      onGenerate(selectedDepth);
    }
  };

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {/* 深度选择器 */}
      <Select
        value={selectedDepth}
        onValueChange={(value) => setSelectedDepth(value as 'brief' | 'detailed')}
        disabled={isGenerating}
      >
        <SelectTrigger className="w-[140px]">
          <SelectValue placeholder="选择摘要深度" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="brief">简要摘要</SelectItem>
          <SelectItem value="detailed">详细摘要</SelectItem>
        </SelectContent>
      </Select>

      {/* 生成/重新生成按钮 */}
      <Button
        onClick={handleGenerate}
        disabled={isGenerating}
        variant={hasSummary ? 'outline' : 'default'}
        className="gap-2"
      >
        {isGenerating ? (
          <>
            <RefreshCw className="h-4 w-4 animate-spin" />
            生成中...
          </>
        ) : hasSummary ? (
          <>
            <RefreshCw className="h-4 w-4" />
            重新生成
          </>
        ) : (
          <>
            <Sparkles className="h-4 w-4" />
            生成摘要
          </>
        )}
      </Button>
    </div>
  );
};

export default SummaryControls;
