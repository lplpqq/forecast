import { BASE_URL, City, SearchCitiesResponse } from '@/schema';
import { Autocomplete, Loader } from '@mantine/core';
import { IconSearch } from '@tabler/icons-react';
import { PropsWithChildren, useEffect, useMemo, useState } from 'react';

const searchCities = async (query: string) => {
  const params = new URLSearchParams({ query });
  const response = await fetch(`${BASE_URL}/cities/search?${params}`, {
    'method': 'GET'
  });

  const results: SearchCitiesResponse = await response.json();
  return results;
};

const MIN_LENGTH = 3;

interface SearchBarProps {
  dataChangeHandler: (city: City) => void
}

const SearchBar = ({
  dataChangeHandler
}: PropsWithChildren<SearchBarProps>) => {
  const [value, setValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<City[]>([]);
  const [selectedCity, setSelectedCity] = useState<City | null>();

  const displayData = useMemo(() => {
    return data.map(city => `${city.name}, ${city.country}`)
  }, [data])

  useEffect(() => {
    if (!selectedCity) return;

    dataChangeHandler(selectedCity)
  }, [selectedCity, dataChangeHandler])

  const handleChange = (newValue: string) => {
    if (displayData.includes(newValue)) {
      setSelectedCity(data[displayData.indexOf(newValue)]);
    }

    setValue(newValue);

    const trimmed = newValue.trim()

    if (trimmed.length < MIN_LENGTH) {
      setData([])

      return;
    }

    setLoading(true);

    searchCities(trimmed).then((result) => {
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
