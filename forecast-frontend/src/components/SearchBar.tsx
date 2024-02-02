import { Autocomplete, Loader } from '@mantine/core';
import { IconSearch } from '@tabler/icons-react';
import { useMemo, useState } from 'react';

interface City {
  name: string;
  country: string;
}

interface SearchCitiesResponse {
  cities: City[]
}

const searchCities = async (query: string) => {
  const params = new URLSearchParams({ query });
  const response = await fetch(`http://localhost:8080/cities/search?${params}`, {
    'method': 'GET'
  });

  const results: SearchCitiesResponse = await response.json();
  return results;
}

const MIN_LENGTH = 3;

const SearchBar = () => {
  const [value, setValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<City[]>([]);

  const displayData = useMemo(() => {
    return data.map(city => `${city.name}, ${city.country}`)
  }, [data])

  const handleChange = (newValue: string) => {
    setValue(newValue);

    const trimmed = newValue.trim()

    if (trimmed.length < MIN_LENGTH) {
      setData([])
      return;
    }

    setLoading(true);

    searchCities(trimmed).then((result) => {
      console.log(result)
      setData(result.cities)

      setLoading(false);
    });
  };

  return (
    <Autocomplete
      className='w-full'
      leftSection={<IconSearch size={20} />}
      value={value}
      data={displayData}
      onChange={handleChange}
      rightSection={loading ? <Loader size="1rem" /> : null}
      size='lg'
      radius={16}
      placeholder="Your favourite city"
    />
  );
}

export default SearchBar;
