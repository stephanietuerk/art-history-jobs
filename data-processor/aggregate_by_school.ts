import { ascending, descending } from 'https://cdn.skypack.dev/d3-array';
import { readCSVObjects } from 'https://deno.land/x/csv/mod.ts';
import { writeJsonSync } from 'https://deno.land/x/jsonfile/mod.ts';

interface JobDatum {
  id: string;
  year: string;
  country: string;
  institution: string;
  tenure: string;
  rank: string;
  field: string;
}

function transformIsTt(isTt: string): string {
  if (isTt.toLowerCase() === 'true') {
    return 'Tenure track';
  } else if (isTt.toLowerCase() === 'false') {
    return 'Non-tenure track';
  } else if (isTt.toLowerCase() === 'unknown') {
    return 'Unknown';
  } else {
    return '';
  }
}

const f = await Deno.open('./data/main/main_data.csv');
const data: JobDatum[] = [];
for await (const row of readCSVObjects(f)) {
  const obj: JobDatum = {} as JobDatum;
  obj.id = row['id\r'] ? row['id\r'].replace(/[\r\n]/g, '') : row.id;
  obj.year = row.year;
  obj.country = row.country;
  obj.institution = row.institution;
  obj.tenure = transformIsTt(
    row.is_tt,
  );
  obj.rank = row.rank;
  obj.field = row.field;
  data.push(obj);
}
f.close();

const dropPostdocs = true;
const countries = [...new Set(data.map((x) => x.country))];
const years = [...new Set(data.map((x) => x.year))];
const dataByCountry = countries.map((country) => {
  const dataForCountry = data.filter((x) => x.country === country);
  const schools = [...new Set(dataForCountry.map((x) => x.institution))].sort(
    (a, b) => ascending(a, b),
  );
  const dataBySchool = schools.map((school) => {
    const dataForSchool = dataForCountry.filter(
      (x) => x.institution === school,
    );
    const jobsByYear = years.map((year) => {
      const jobsForYear = dataForSchool.filter((x) => x.year === year);
      const ids = [...new Set(jobsForYear.map((x) => x.id))];
      const jobsById = ids.map((id) => {
        const jobsForId = jobsForYear.filter((x) => x.id === id);
        // testing here -- if all don't add up to one, throw warning
        return {
          id,
          tenure: jobsForId[0].tenure,
          rank: [...new Set(jobsForId.map((x) => x.rank))],
          field: jobsForId.map((x) => x.field),
        };
      });
      let filteredJobs = jobsById;
      if (
        dropPostdocs && jobsById.length > 0 &&
        jobsById.some((x) => x.rank.some((y) => y.toLowerCase() === 'postdoc'))
      ) {
        filteredJobs = jobsById.filter((x) =>
          x.rank.every((y) => y.toLowerCase() === 'postdoc') ? false : true
        );
      }
      return {
        year: year,
        jobs: filteredJobs,
      };
    });
    return {
      school,
      jobsByYear,
    };
  }).filter((x) => x.jobsByYear.some((y) => y.jobs.length > 0));
  return {
    country: country === 'US' ? 'United States' : country,
    jobsBySchool: dataBySchool,
  };
});
dataByCountry
  .sort((a, b) => ascending(a.country, b.country))
  .sort((a, b) => descending(a.jobsBySchool.length, b.jobsBySchool.length));
writeJsonSync('./data/main/main_data_by_school.json', dataByCountry);
