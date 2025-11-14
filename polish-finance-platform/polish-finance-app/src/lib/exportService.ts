/**
 * Export Service
 * Handles exporting data to CSV and JSON formats
 */

export interface ExportableCompany {
  symbol: string;
  company_name: string;
  current_price: number;
  change_percent: number;
  pe_ratio: number | null;
  pb_ratio: number | null;
  trading_volume: string;
  score?: number;
}

export function exportToCSV(companies: ExportableCompany[], filename: string = 'wig80_data'): void {
  const headers = ['Symbol', 'Nazwa', 'Cena', 'Zmiana %', 'P/E', 'P/B', 'Wolumen', 'Ocena'];
  const rows = companies.map(company => [
    company.symbol,
    company.company_name,
    company.current_price.toFixed(2),
    company.change_percent.toFixed(2),
    company.pe_ratio?.toFixed(2) || 'N/A',
    company.pb_ratio?.toFixed(2) || 'N/A',
    company.trading_volume,
    company.score?.toFixed(0) || 'N/A'
  ]);

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n');

  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}_${new Date().toISOString().split('T')[0]}.csv`);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  URL.revokeObjectURL(url);
}

export function exportToJSON(companies: ExportableCompany[], filename: string = 'wig80_data'): void {
  const data = {
    exportDate: new Date().toISOString(),
    totalCompanies: companies.length,
    companies: companies.map(company => ({
      symbol: company.symbol,
      company_name: company.company_name,
      current_price: company.current_price,
      change_percent: company.change_percent,
      pe_ratio: company.pe_ratio,
      pb_ratio: company.pb_ratio,
      trading_volume: company.trading_volume,
      score: company.score
    }))
  };

  const jsonContent = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonContent], { type: 'application/json' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}_${new Date().toISOString().split('T')[0]}.json`);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  URL.revokeObjectURL(url);
}

