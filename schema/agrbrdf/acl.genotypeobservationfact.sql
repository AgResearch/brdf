--
-- Name: genotypeobservationfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE genotypeobservationfact FROM PUBLIC;
REVOKE ALL ON TABLE genotypeobservationfact FROM agrbrdf;
GRANT ALL ON TABLE genotypeobservationfact TO agrbrdf;
GRANT SELECT ON TABLE genotypeobservationfact TO gbs;


