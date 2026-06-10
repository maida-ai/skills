def fail($message): error("get-stack-review-context: \($message)");

def comment_summary:
  {
    id,
    url,
    author: .author.login,
    body: .bodyText,
    createdAt,
    updatedAt,
    path,
    line: (.line // .originalLine),
    diffHunk,
    pullRequestReview: .pullRequestReview
  };

.[0].data.repository.pullRequest as $pr

| if ($pr.commits.totalCount // 0) > ($pr.commits.nodes | length) then
    fail("PR has \($pr.commits.totalCount) commits, but this helper fetched \($pr.commits.nodes | length); commit pagination is not yet supported")
  elif any(.[] | .data.repository.pullRequest.reviewThreads.nodes[]?; ((.comments.totalCount // 0) > (.comments.nodes | length))) then
    fail("at least one review thread has more comments than fetched; nested comment pagination is not yet supported")
  else
    .
  end

| (
    $pr.commits.nodes
    | to_entries
    | map({
        oid: .value.commit.oid,
        short: .value.commit.abbreviatedOid,
        subject: .value.commit.messageHeadline,
        message: .value.commit.message,
        committedDate: .value.commit.committedDate,
        url: .value.commit.url,
        order: .key
      })
  ) as $current_commits

| (
    $current_commits
    | sort_by(.subject)
    | group_by(.subject)
    | map(select(length > 1) | .[0].subject)
  ) as $duplicate_subjects

| if $allow_subject_mapping and ($duplicate_subjects | length) > 0 then
    fail("commit subjects are not unique: \($duplicate_subjects | join(", "))")
  else
    .
  end

| (
    $current_commits
    | map({key: .oid, value: .})
    | from_entries
  ) as $by_oid

| (
    $current_commits
    | map({key: .subject, value: .})
    | from_entries
  ) as $by_subject

| [
    .[]
    | .data.repository.pullRequest.reviewThreads.nodes[]?
    | . as $thread
    | ($thread.comments.nodes | sort_by(.createdAt)) as $comments
    | ($comments[0] // null) as $root
    | select($root != null)
    | (
        if $by_oid[$root.originalCommit.oid] != null then
          {commit: $by_oid[$root.originalCommit.oid], reason: "original_sha"}
        elif $by_oid[$root.commit.oid] != null then
          {commit: $by_oid[$root.commit.oid], reason: "current_sha"}
        elif $allow_subject_mapping and $by_subject[$root.originalCommit.messageHeadline] != null then
          {commit: $by_subject[$root.originalCommit.messageHeadline], reason: "original_subject"}
        elif $allow_subject_mapping and $by_subject[$root.commit.messageHeadline] != null then
          {commit: $by_subject[$root.commit.messageHeadline], reason: "current_subject"}
        else
          {commit: null, reason: "unmatched"}
        end
      ) as $mapping
    | {
        thread_id: $thread.id,
        report_commit: (if $mapping.commit != null then $mapping.commit.oid else ($root.originalCommit.oid // $root.commit.oid) end),
        report_short_commit: (if $mapping.commit != null then $mapping.commit.short else ($root.originalCommit.abbreviatedOid // $root.commit.abbreviatedOid) end),
        report_subject: (if $mapping.commit != null then $mapping.commit.subject else ($root.originalCommit.messageHeadline // $root.commit.messageHeadline) end),
        commit_order: (if $mapping.commit != null then $mapping.commit.order else 999999 end),
        is_current_commit: ($mapping.commit != null),
        mapping_reason: $mapping.reason,
        path: ($root.path // $thread.path),
        line: ($root.line // $root.originalLine // $thread.line),
        startLine: $thread.startLine,
        isResolved: $thread.isResolved,
        isOutdated: $thread.isOutdated,
        subjectType: $thread.subjectType,
        initial_comment: ($root | comment_summary),
        replies: ($comments[1:] | map(comment_summary)),
        comment_count: ($comments | length)
      }
  ] as $threads

| {
    pull_request: {
      number: $pr.number,
      title: $pr.title,
      url: $pr.url,
      baseRefName: $pr.baseRefName,
      headRefName: $pr.headRefName
    },
    commits: (
      $current_commits
      | map(. as $commit | . + {
          threads: (
            $threads
            | map(select(.report_commit == $commit.oid))
            | sort_by(.path, (.line // 0), .initial_comment.createdAt)
          )
        })
    ),
    unmatched_threads: (
      $threads
      | map(select(.is_current_commit == false))
      | sort_by(.report_short_commit, .path, (.line // 0))
    )
  }
