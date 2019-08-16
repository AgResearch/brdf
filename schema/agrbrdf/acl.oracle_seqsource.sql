--
-- Name: oracle_seqsource; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE oracle_seqsource FROM PUBLIC;
REVOKE ALL ON TABLE oracle_seqsource FROM agrbrdf;
GRANT ALL ON TABLE oracle_seqsource TO agrbrdf;
GRANT SELECT ON TABLE oracle_seqsource TO gbs;


