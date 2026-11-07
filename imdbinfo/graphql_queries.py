"""Query document used by the alternate title-details service."""

MOVIE_QUERY = """
query Title($id: ID!) {
  title(id: $id) {
    id
    titleText {
      text
    }
    originalTitleText {
      text
    }
    titleType {
      id
    }
    releaseYear {
      year
      endYear
    }
    ratingsSummary {
      aggregateRating
      voteCount
    }
    certificates(first: 100) {
      edges {
        node {
          id
          rating
          ratingReason
          country {
            id
            text
          }
          ratingsBody {
            id
          }
          attributes {
            text
          }
        }
      }
    }
    runtime {
      seconds
    }
    primaryImage {
      url
    }
    plot {
      plotText {
        plainText
      }
    }
    genres {
      genres {
        text
      }
    }
    releaseDate {
      day
      month
      year
    }
    interests(first: 20) {
      edges {
        node {
          primaryText {
            text
          }
        }
      }
    }
    principalCreditsV2 {
      credits {
        name {
          id
          nameText {
            text
          }
        }
      }
      grouping {
        groupingId
      }
    }
    credits(first: 250) {
      edges {
        node {
          __typename
          name {
            id
            nameText {
              text
            }
          }
          category {
            id
            text
          }
          ... on Cast {
            characters {
              name
            }
            attributes {
              text
            }
          }
          ... on Crew {
            jobs {
              text
            }
          }
        }
      }
    }
    wins: awardNominations(first: 1, filter: { wins: WINS_ONLY }) {
      total
    }
    nominationsExcludeWins: awardNominations(
      first: 1
      filter: { wins: EXCLUDE_WINS }
    ) {
      total
    }
    prestigiousAwardSummary {
      nominations
      wins
      awardNomination {
        award {
          text
        }
      }
    }
    metacritic {
      metascore {
        score
      }
    }
    worldwideGross: lifetimeGross(boxOfficeArea: WORLDWIDE) {
      total {
        amount
        currency
      }
    }
    productionBudget {
      budget {
        amount
        currency
      }
    }
    primaryVideos(first: 5) {
      edges {
        node {
          id
        }
      }
    }
    filmingLocations(first: 10) {
      edges {
        node {
          text
        }
      }
    }
    countriesOfOrigin {
      countries {
        id
        text
      }
    }
    keywords(first: 10) {
      edges {
        node {
          keyword {
            text {
              text
            }
          }
        }
      }
    }
    companyCredits(first: 100) {
      edges {
        node {
          company {
            id
            companyText {
              text
            }
          }
          category {
            id
            text
          }
          countries {
            text
          }
          attributes {
            text
          }
          displayableProperty {
            value {
              plainText
            }
          }
        }
      }
    }
    technicalSpecifications {
      soundMixes {
        items {
          text
        }
      }
      colorations {
        items {
          text
        }
      }
      aspectRatios {
        items {
          aspectRatio
          attributes {
            text
          }
        }
      }
      cameras {
        items {
          camera
        }
      }
      laboratories {
        items {
          laboratory
        }
      }
      negativeFormats {
        items {
          negativeFormat
        }
      }
      printedFormats {
        items {
          printedFormat
        }
      }
      processes {
        items {
          process
        }
      }
    }
    spokenLanguages {
      spokenLanguages {
        id
        text
      }
    }
    akas(first: 10) {
      edges {
        node {
          text
        }
      }
    }
    series {
      series {
        id
        titleText {
          text
        }
        originalTitleText {
          text
        }
      }
      episodeNumber {
        episodeNumber
        seasonNumber
      }
    }
    episodes {
      displayableSeasons(first: 100) {
        edges {
          node {
            season
          }
        }
      }
      displayableYears(first: 100) {
        edges {
          node {
            year
          }
        }
      }
    }
    summaries: plots(first: 5, filter: { type: [SUMMARY] }) {
      edges {
        node {
          plotText {
            plaidHtml
          }
        }
      }
    }
    synopses: plots(first: 2, filter: { type: [SYNOPSIS] }) {
      edges {
        node {
          plotText {
            plaidHtml
          }
        }
      }
    }
  }
}
"""
