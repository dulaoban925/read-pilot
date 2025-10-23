/**
 * 摘要加载状态组件
 * 显示摘要生成中的加载动画和状态信息
 */
'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { Loader2 } from 'lucide-react';

export interface LoadingSummaryProps {
  /** 加载提示文本 */
  message?: string;
  /** 自定义类名 */
  className?: string;
}

export const LoadingSummary: React.FC<LoadingSummaryProps> = ({
  message = 'AI 正在分析文档,生成摘要...',
  className = '',
}) => {
  return (
    <Card className={`w-full ${className}`}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Loader2 className="h-5 w-5 animate-spin text-primary" />
            生成摘要中
          </CardTitle>
        </div>
        <CardDescription>{message}</CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* 概述骨架 */}
        <div className="space-y-2">
          <Skeleton className="h-5 w-20" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
        </div>

        {/* 分隔线 */}
        <div className="border-t" />

        {/* 关键见解骨架 */}
        <div className="space-y-3">
          <Skeleton className="h-5 w-24" />
          <div className="space-y-2">
            <div className="flex items-start gap-2">
              <Skeleton className="h-1.5 w-1.5 rounded-full mt-1.5 flex-shrink-0" />
              <Skeleton className="h-4 flex-1" />
            </div>
            <div className="flex items-start gap-2">
              <Skeleton className="h-1.5 w-1.5 rounded-full mt-1.5 flex-shrink-0" />
              <Skeleton className="h-4 flex-1" />
            </div>
            <div className="flex items-start gap-2">
              <Skeleton className="h-1.5 w-1.5 rounded-full mt-1.5 flex-shrink-0" />
              <Skeleton className="h-4 w-2/3" />
            </div>
          </div>
        </div>

        {/* 分隔线 */}
        <div className="border-t" />

        {/* 主要概念骨架 */}
        <div className="space-y-3">
          <Skeleton className="h-5 w-24" />
          <div className="flex flex-wrap gap-2">
            <Skeleton className="h-7 w-20" />
            <Skeleton className="h-7 w-24" />
            <Skeleton className="h-7 w-16" />
            <Skeleton className="h-7 w-28" />
            <Skeleton className="h-7 w-20" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default LoadingSummary;
