/**
 * 文档摘要显示组件
 * 显示 AI 生成的文档摘要,包括抽象、关键见解和主要概念
 */
'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Separator } from '@/components/ui/Separator';

export interface Summary {
  id: string;
  document_id: string;
  abstract: string;
  key_insights: string[];
  main_concepts: string[];
  depth_level: 'brief' | 'detailed';
  model_used: string;
  created_at: string;
  updated_at: string;
}

export interface SummaryDisplayProps {
  summary: Summary;
  className?: string;
}

export const SummaryDisplay: React.FC<SummaryDisplayProps> = ({ summary, className = '' }) => {
  return (
    <Card className={`w-full ${className}`}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>文档摘要</CardTitle>
          <div className="flex gap-2">
            <Badge variant={summary.depth_level === 'detailed' ? 'default' : 'secondary'}>
              {summary.depth_level === 'detailed' ? '详细' : '简要'}
            </Badge>
            <Badge variant="outline">{summary.model_used}</Badge>
          </div>
        </div>
        <CardDescription>
          生成时间: {new Date(summary.created_at).toLocaleString('zh-CN')}
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* 摘要抽象 */}
        <div>
          <h3 className="text-lg font-semibold mb-2">概述</h3>
          <p className="text-muted-foreground leading-relaxed">{summary.abstract}</p>
        </div>

        <Separator />

        {/* 关键见解 */}
        {summary.key_insights && summary.key_insights.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold mb-3">关键见解</h3>
            <ul className="space-y-2">
              {summary.key_insights.map((insight, index) => (
                <li key={index} className="flex items-start">
                  <span className="mr-2 mt-1 flex-shrink-0 h-1.5 w-1.5 rounded-full bg-primary" />
                  <span className="text-muted-foreground">{insight}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <Separator />

        {/* 主要概念 */}
        {summary.main_concepts && summary.main_concepts.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold mb-3">主要概念</h3>
            <div className="flex flex-wrap gap-2">
              {summary.main_concepts.map((concept, index) => (
                <Badge key={index} variant="secondary" className="px-3 py-1">
                  {concept}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default SummaryDisplay;
