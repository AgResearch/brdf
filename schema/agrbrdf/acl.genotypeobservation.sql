--
-- Name: genotypeobservation; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE genotypeobservation FROM PUBLIC;
REVOKE ALL ON TABLE genotypeobservation FROM agrbrdf;
GRANT ALL ON TABLE genotypeobservation TO agrbrdf;
GRANT SELECT ON TABLE genotypeobservation TO gbs;


