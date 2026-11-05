%% Cuba, NM drinking water (PWSID NM3509023) -- MATLAB starter plots for ENG220
% Run from this folder (the one that contains data/).  Needs MATLAB R2020a or newer (exportgraphics).
% Every CSV loads with readtable; dates are converted with datetime.

clear; close all;
dataDir = fullfile(pwd, 'data');
figDir  = fullfile(pwd, 'figures_matlab');
if ~exist(figDir, 'dir'), mkdir(figDir); end
rd = @(f) readtable(fullfile(dataDir, f), 'TextType', 'string');

LIMIT = [0.816 0.231 0.231];               % red for regulatory reference lines
BLUE  = [0.165 0.471 0.839];
ORNG  = [0.922 0.408 0.204];
AQUA  = [0.106 0.686 0.478];

%% 1. Violations per year (all years)
v = rd('violations_all_years.csv');
yrs = (min(v.year):max(v.year))';
cats = ["Contaminant limit exceeded (health-based)", "Treatment technique (health-based)", ...
        "Monitoring & reporting", "Reporting (CCR)", "Public notice / communication", ...
        "Operations / staffing", "Other"];
counts = zeros(numel(yrs), numel(cats));
for j = 1:numel(cats)
    counts(:, j) = histcounts(v.year(v.category == cats(j)), [yrs; yrs(end)+1]);
end
figure('Position', [100 100 1000 420]);
bar(yrs, counts, 'stacked', 'EdgeColor', 'w');
legend(cats, 'Location', 'northwest', 'Box', 'off');
ylabel('Number of violations'); grid on;
title('Cuba Water System: violations by year determined (2026 = Jan-Oct)');
exportgraphics(gcf, fullfile(figDir, '01_violations_by_year.png'), 'Resolution', 200);

%% 2. Chlorine residual, monthly
cl = rd('chlorine_residual_monthly_2025_2026.csv');
cl.month_start = toDT(cl.month_start);
figure('Position', [100 100 1000 380]);
plot(cl.month_start, cl.monthly_avg_mg_L, '-o', 'Color', BLUE, 'LineWidth', 2, 'MarkerFaceColor', BLUE); hold on;
plot(cl.month_start, cl.running_annual_avg_mg_L, '-', 'Color', ORNG, 'LineWidth', 2);
yline(0.2, '--', '0.2 mg/L WHO minimum residual guideline', 'Color', LIMIT, 'LabelHorizontalAlignment', 'left');
ylim([0 1.15]); ylabel('Chlorine residual (mg/L)'); grid on;
legend('Monthly average', 'Running annual average', 'Location', 'northeast', 'Box', 'off');
title('Disinfectant (chlorine) residual, 2025-2026');
exportgraphics(gcf, fullfile(figDir, '03_chlorine_residual.png'), 'Resolution', 200);

%% 3. Lead & copper 90th percentile history
pb = rd('lead_copper_90th_percentile_history.csv');
pb.last_sample_date = toDT(pb.last_sample_date);
figure('Position', [100 100 1100 380]);
an = ["LEAD", "COPPER"]; al = [0.015 1.3]; col = {BLUE, AQUA};
for k = 1:2
    subplot(1, 2, k);
    s = pb(pb.analyte == an(k), :);
    plot(s.last_sample_date, s.x90th_percentile, '-o', 'Color', col{k}, 'LineWidth', 2, 'MarkerFaceColor', col{k});
    yline(al(k), '--', sprintf('Action level %g mg/L', al(k)), 'Color', LIMIT, 'LabelHorizontalAlignment', 'left');
    ylim([0 al(k)*1.25]); ylabel('mg/L'); grid on;
    title(sprintf('%s - 90th percentile of tap samples', an(k)));
end
exportgraphics(gcf, fullfile(figDir, '04_lead_copper_90th_percentile.png'), 'Resolution', 200);
% NOTE: readtable renames the column "90th_percentile" to "x90th_percentile" because
% MATLAB variable names cannot start with a digit.

%% 4. Lead in individual tap samples
lc = rd('lead_copper_tap_samples_2025_2026.csv');
lc.sample_date = toDT(lc.sample_date);
lead = lc(lc.analyte == "LEAD", :);
det = toBool(lead.detected);
figure('Position', [100 100 1000 380]);
scatter(lead.sample_date(det), 1000*lead.result_mg_L(det), 50, BLUE, 'filled'); hold on;
scatter(lead.sample_date(~det), zeros(sum(~det),1), 50, [0.54 0.53 0.51], 'v');
yline(15, '--', 'Lead action level 15 ug/L (applies to 90th percentile)', 'Color', LIMIT, 'LabelHorizontalAlignment', 'left');
ylabel('Lead (ug/L)'); ylim([-1.5 24]); grid on;
legend('Detected', 'Not detected', 'Location', 'northeast', 'Box', 'off');
title('Lead in individual household tap samples, 2025-2026');
exportgraphics(gcf, fullfile(figDir, '05_lead_tap_samples.png'), 'Resolution', 200);

%% 5. Detected contaminants as % of their limit
d = rd('chemical_detections_2025_2026.csv');
d = d(~isnan(d.pct_of_limit), :);
d.sample_date = toDT(d.sample_date);
d = sortrows(d, 'sample_date', 'descend');
[~, keep] = unique(d.analyte, 'stable');          % latest result per analyte
d = sortrows(d(keep, :), 'pct_of_limit');
figure('Position', [100 100 1000 480]);
b = barh(categorical(d.analyte, d.analyte), d.pct_of_limit, 'FaceColor', 'flat', 'EdgeColor', 'w');
isMCL = startsWith(d.limit_type, "MCL");
b.CData(isMCL, :)  = repmat(BLUE, sum(isMCL), 1);
b.CData(~isMCL, :) = repmat(ORNG, sum(~isMCL), 1);
set(gca, 'XScale', 'log'); grid on;
xline(100, '--', '100% = at the limit', 'Color', LIMIT);
xlabel('Result as % of its limit (log scale)  -- blue = health MCL, orange = secondary standard');
title('Detected contaminants, latest 2025-2026 result vs. its standard');
exportgraphics(gcf, fullfile(figDir, '06_detections_vs_limits.png'), 'Resolution', 200);

%% 6. Quick numbers for your slides
v2 = rd('violations_2025_2026.csv');
fprintf('2025-26 violations: %d  (open: %d, health-based: %d)\n', height(v2), ...
    sum(startsWith(v2.status, "Open")), sum(v2.health_based == "Y"));
tcr = rd('coliform_bacteria_samples_2025_2026.csv');
fprintf('Coliform samples: %d  (positives: %d)\n', height(tcr), sum(tcr.total_coliform_present));
pen = rd('nmed_2026_penalty_breakdown.csv');
fprintf('NMED July 2026 penalty total: $%s\n', num2str(sum(pen.penalty_usd)));

%% ---- local helper functions (must stay at the end of the script)
function x = toDT(x)
% readtable may already return datetime; convert only if it came in as text
if ~isdatetime(x), x = datetime(x, 'InputFormat', 'yyyy-MM-dd'); end
end

function b = toBool(x)
% "True"/"False" text from Python -> logical (newer MATLAB may already import as logical)
if islogical(x), b = x; else, b = lower(string(x)) == "true"; end
end
