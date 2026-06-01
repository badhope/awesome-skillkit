"use client";

import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart as RechartsBarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
} from "recharts";
import type { PieLabelRenderProps } from "recharts";
import { cn } from "@/lib/utils";
import type { UsageTrend, CategoryDistribution, PopularSkill } from "@/types";

const CHART_COLORS = [
  "hsl(262 83% 58%)",
  "hsl(173 80% 36%)",
  "hsl(43 96% 56%)",
  "hsl(0 84% 60%)",
  "hsl(199 89% 48%)",
  "hsl(280 65% 60%)",
  "hsl(150 60% 45%)",
  "hsl(30 90% 55%)",
];

interface ChartContainerProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  className?: string;
}

function ChartContainer({ title, subtitle, children, className }: ChartContainerProps) {
  return (
    <div className={cn("rounded-xl border bg-card p-6", className)}>
      <div className="mb-4">
        <h3 className="font-semibold">{title}</h3>
        {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
      </div>
      <div className="h-[300px]">{children}</div>
    </div>
  );
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ value: number; name: string; color: string }>;
  label?: string;
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload) return null;
  return (
    <div className="rounded-lg border bg-background p-3 shadow-xl">
      <p className="text-sm font-medium mb-1">{label}</p>
      {payload.map((entry, index) => (
        <div key={index} className="flex items-center gap-2 text-sm">
          <div
            className="h-2.5 w-2.5 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-muted-foreground">{entry.name}:</span>
          <span className="font-medium">{entry.value.toLocaleString()}</span>
        </div>
      ))}
    </div>
  );
}

interface UsageTrendChartProps {
  data: UsageTrend[];
}

export function UsageTrendChart({ data }: UsageTrendChartProps) {
  const formattedData = data.map((item) => ({
    ...item,
    date: new Date(item.date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
  }));

  return (
    <ChartContainer title="Usage Trends" subtitle="Daily usage over time">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={formattedData} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="colorDownloads" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={CHART_COLORS[0]} stopOpacity={0.3} />
              <stop offset="95%" stopColor={CHART_COLORS[0]} stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorViews" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={CHART_COLORS[1]} stopOpacity={0.3} />
              <stop offset="95%" stopColor={CHART_COLORS[1]} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            className="text-muted-foreground text-xs"
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 12 }}
            className="text-muted-foreground text-xs"
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Area
            type="monotone"
            dataKey="downloads"
            stroke={CHART_COLORS[0]}
            fill="url(#colorDownloads)"
            strokeWidth={2}
            name="Downloads"
          />
          <Area
            type="monotone"
            dataKey="views"
            stroke={CHART_COLORS[1]}
            fill="url(#colorViews)"
            strokeWidth={2}
            name="Views"
          />
        </AreaChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}

interface PopularSkillsChartProps {
  data: PopularSkill[];
}

export function PopularSkillsChart({ data }: PopularSkillsChartProps) {
  const chartData = data.slice(0, 8).map((item) => ({
    name: item.skill.name.length > 15 ? item.skill.name.slice(0, 15) + "..." : item.skill.name,
    uses: item.use_count,
    rating: item.rating,
  }));

  return (
    <ChartContainer title="Popular Skills" subtitle="Most used skills">
      <ResponsiveContainer width="100%" height="100%">
        <RechartsBarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" horizontal={false} />
          <XAxis
            type="number"
            tick={{ fontSize: 12 }}
            className="text-muted-foreground text-xs"
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            dataKey="name"
            type="category"
            tick={{ fontSize: 12 }}
            className="text-muted-foreground text-xs"
            axisLine={false}
            tickLine={false}
            width={120}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="uses" fill={CHART_COLORS[2]} radius={[0, 4, 4, 0]} name="Uses" />
        </RechartsBarChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}

interface CategoryDistributionChartProps {
  data: CategoryDistribution[];
}

export function CategoryDistributionChart({ data }: CategoryDistributionChartProps) {
  const chartData = data.map((item) => ({
    name: item.category_name,
    value: item.skill_count,
    percentage: item.percentage,
  }));

  const RADIAN = Math.PI / 180;
  const renderCustomizedLabel = ({
    cx = 0,
    cy = 0,
    midAngle = 0,
    innerRadius = 0,
    outerRadius = 0,
    percent = 0,
  }: PieLabelRenderProps) => {
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);
    if (percent < 0.05) return null;
    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor="middle"
        dominantBaseline="central"
        fontSize={12}
        fontWeight={600}
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  return (
    <ChartContainer title="Category Distribution" subtitle="Skills per category">
      <ResponsiveContainer width="100%" height="100%">
        <RechartsPieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderCustomizedLabel}
            outerRadius={110}
            innerRadius={50}
            dataKey="value"
            paddingAngle={2}
          >
            {chartData.map((_, index) => (
              <Cell
                key={index}
                fill={CHART_COLORS[index % CHART_COLORS.length]}
                stroke="hsl(var(--background))"
                strokeWidth={2}
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </RechartsPieChart>
      </ResponsiveContainer>
      <div className="flex flex-wrap justify-center gap-3 mt-4">
        {chartData.map((item, index) => (
          <div key={item.name} className="flex items-center gap-1.5 text-xs">
            <div
              className="h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }}
            />
            <span className="text-muted-foreground">{item.name}</span>
          </div>
        ))}
      </div>
    </ChartContainer>
  );
}

interface StatsOverviewChartProps {
  totalSkills: number;
  totalCompositions: number;
  totalUsers: number;
  totalDownloads: number;
}

export function StatsOverviewChart({
  totalSkills,
  totalCompositions,
  totalUsers,
  totalDownloads,
}: StatsOverviewChartProps) {
  const chartData = [
    { name: "Skills", value: totalSkills },
    { name: "Compositions", value: totalCompositions },
    { name: "Users", value: totalUsers },
    { name: "Downloads", value: totalDownloads },
  ];

  return (
    <ChartContainer title="Platform Overview" subtitle="Key metrics at a glance">
      <ResponsiveContainer width="100%" height="100%">
        <RechartsBarChart data={chartData} margin={{ top: 20, right: 20, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
          <XAxis
            dataKey="name"
            tick={{ fontSize: 14 }}
            className="text-muted-foreground"
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 12 }}
            className="text-muted-foreground text-xs"
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="value" radius={[8, 8, 0, 0]} maxBarSize={60}>
            {chartData.map((_, index) => (
              <Cell
                key={index}
                fill={CHART_COLORS[index % CHART_COLORS.length]}
                fillOpacity={0.85}
              />
            ))}
          </Bar>
        </RechartsBarChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}